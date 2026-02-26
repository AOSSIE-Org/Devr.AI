from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = settings.database_url

if not DATABASE_URL:
    logger.warning("DATABASE_URL is not set. Database connection pooling will not be available.")
    # Fallback or strict error depending on requirements. 
    # For now ensuring tests/code doesn't crash on import if env missing during build.
    # But initialization should be guarded.

# Initialize SQLAlchemy Async Engine with pooling
# If DATABASE_URL is missing, engine will be None and get_db will fail/error out appropriately when called
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,  # Maintain 20 open connections
    max_overflow=10,  # Allow 10 extra during spikes
    pool_timeout=30,  # Wait 30s for a connection before raising timeout
    pool_pre_ping=True,  # Check connection health before handing it out
) if DATABASE_URL else None

# Session Factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
) if engine else None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide a thread-safe database session.
    Ensures that the session is closed after the request is processed.
    """
    if not async_session_maker:
        raise RuntimeError("Database engine is not initialized. check DATABASE_URL.")
    
    async with async_session_maker() as session:
        try:
            yield session
            # automatic commit/rollback is often handled by caller or service layer logic
        except Exception:
            logger.exception("Database session error")
            await session.rollback()
            raise
        # session.close() is handled automatically by the async context manager
