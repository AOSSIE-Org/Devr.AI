from sqlalchemy.ext.asyncio import create_async_engine
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import importlib
from app.core import config

# We need to reload the module to pick up the patched settings because 
# engine is created at module level in app.database.core.

@pytest.fixture
def mock_db_module():
    """
    Fixture to reload app.database.core with patched settings.
    """
    # Patch the settings object where it is defined or imported
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.database_url = "postgresql+asyncpg://user:password@localhost:5432/testdb"
        
        # Reload the module so 'engine' is recreated with the new settings
        import app.database.core
        importlib.reload(app.database.core)
        
        yield app.database.core

@pytest.mark.asyncio
async def test_connection_pooling_configuration(mock_db_module):
    """
    Verify that the engine is configured with the expected pool size.
    """
    engine = mock_db_module.engine
    
    if engine:
        assert engine.pool.size() == 20
        assert engine.pool.timeout() == 30
    else:
        pytest.fail("Engine not initialized")

@pytest.mark.asyncio
async def test_concurrent_session_acquisition(mock_db_module):
    """
    Simulate high concurrency to ensure sessions can be acquired without error.
    """
    # Mock the session
    mock_session = MagicMock()
    # Ensure close and rollback return awaitables (Futures)
    mock_session.close = MagicMock(return_value=asyncio.Future())
    mock_session.close.return_value.set_result(None)
    mock_session.rollback = MagicMock(return_value=asyncio.Future())
    mock_session.rollback.return_value.set_result(None)
    
    # Mock async context manager: __aenter__ returns session, __aexit__ returns None (awaitable)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Patch the async_session_maker in the RELOADED module
    with patch.object(mock_db_module, "async_session_maker", return_value=mock_session) as mock_maker:
        
        async def task():
            # Use the get_db from the RELOADED module
            async for _session in mock_db_module.get_db():
                # Simulate some work
                await asyncio.sleep(0.01)
                return True
        
        # Run 50 concurrent tasks
        results = await asyncio.gather(*[task() for _ in range(50)])
        
        assert all(results)
        # Verify correct number of calls
        assert mock_maker.call_count == 50
        
        # Automatic closing is handled by the context manager, which calls __aexit__
        assert mock_session.__aexit__.call_count == 50

@pytest.mark.asyncio
async def test_session_rollback_on_error(mock_db_module):
    """
    Ensure rollback is called if an exception occurs during session usage.
    """
    mock_session = MagicMock()
    mock_session.rollback = MagicMock(return_value=asyncio.Future())
    mock_session.rollback.return_value.set_result(None)
    
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch.object(mock_db_module, "async_session_maker", return_value=mock_session):
        with pytest.raises(ValueError):
            async for _session in mock_db_module.get_db():
                raise ValueError("Simulated Error")
        
        # Verify rollback was called once
        assert mock_session.rollback.call_count == 1
        # Verify exit was called (which would handle cleanup in a real scenario)
        assert mock_session.__aexit__.call_count == 1
