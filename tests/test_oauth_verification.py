import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.auth.verification import (
    create_verification_session,
    validate_oauth_state,
    find_user_by_session_and_verify,
    get_verification_session_info,
    _verification_sessions
)

@pytest.fixture(autouse=True)
def clean_sessions():
    _verification_sessions.clear()
    yield
    _verification_sessions.clear()

@pytest.mark.asyncio
async def test_create_verification_session_success():
    mock_supabase = MagicMock()
    mock_execute = AsyncMock()
    mock_execute.data = [{"id": "user-123"}]
    
    mock_table = MagicMock()
    mock_update = MagicMock()
    mock_eq = MagicMock()
    
    mock_supabase.table.return_value = mock_table
    mock_table.update.return_value = mock_update
    mock_update.eq.return_value = mock_eq
    mock_eq.execute = mock_execute

    with patch("app.services.auth.verification.get_supabase_client", return_value=mock_supabase):
        result = await create_verification_session("discord-id-123")
        assert result is not None
        session_id, oauth_state = result
        assert len(session_id) > 0
        assert len(oauth_state) > 0
        
        # Verify it was stored in memory sessions
        assert session_id in _verification_sessions
        discord_id, expiry, state = _verification_sessions[session_id]
        assert discord_id == "discord-id-123"
        assert state == oauth_state

@pytest.mark.asyncio
async def test_validate_oauth_state():
    mock_supabase = MagicMock()
    mock_execute = AsyncMock()
    mock_execute.data = [{"id": "user-123"}]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    with patch("app.services.auth.verification.get_supabase_client", return_value=mock_supabase):
        result = await create_verification_session("discord-id-123")
        assert result is not None
        session_id, oauth_state = result
        
        # Validation with correct state
        assert validate_oauth_state(session_id, oauth_state) is True
        
        # Validation with incorrect state
        assert validate_oauth_state(session_id, "wrong-state") is False
        
        # Validation with missing state
        assert validate_oauth_state(session_id, None) is False
        
        # Validation with non-existent session
        assert validate_oauth_state("wrong-session-id", oauth_state) is False

@pytest.mark.asyncio
async def test_get_verification_session_info():
    mock_supabase = MagicMock()
    mock_execute = AsyncMock()
    mock_execute.data = [{"id": "user-123"}]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute = mock_execute

    with patch("app.services.auth.verification.get_supabase_client", return_value=mock_supabase):
        result = await create_verification_session("discord-id-123")
        assert result is not None
        session_id, _ = result
        
        info = await get_verification_session_info(session_id)
        assert info is not None
        assert info["discord_id"] == "discord-id-123"
        
        # Test expired session
        _verification_sessions[session_id] = (
            "discord-id-123",
            datetime.now() - timedelta(minutes=1),
            "state"
        )
        expired_info = await get_verification_session_info(session_id)
        assert expired_info is None
        assert session_id not in _verification_sessions
