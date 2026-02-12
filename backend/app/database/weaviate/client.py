import weaviate
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import asyncio

logger = logging.getLogger(__name__)

_client = None
_connected = False
_client_lock = None


def get_client():
    """Get or create the global Weaviate client instance."""
    global _client
    if _client is None:
        _client = weaviate.use_async_with_local()
    return _client


def _get_client_lock():
    """Get or create the client lock, binding it to the current event loop."""
    global _client_lock
    if _client_lock is None:
        _client_lock = asyncio.Lock()
    return _client_lock


async def ensure_connected():
    """Ensure the client is connected. Reuses existing connection if available."""
    global _client, _connected
    client = get_client()
    
    if not _connected or not client.is_connected():
        async with _get_client_lock():
            client = get_client()
            if not _connected or not client.is_connected():
                await client.connect()
                _connected = True
                logger.info("Weaviate client connected")
    
    return client


@asynccontextmanager
async def get_weaviate_client() -> AsyncGenerator[weaviate.WeaviateClient, None]:
    """Async context manager for Weaviate client with persistent connection."""
    try:
        client = await ensure_connected()
        yield client
    except Exception as e:
        logger.error("Weaviate client error: %s", e)
        raise


async def close_weaviate_client():
    """Close the Weaviate client. Call this on application shutdown."""
    global _client, _connected
    
    async with _get_client_lock():
        if _client is not None:
            try:
                await _client.close()
                logger.info("Weaviate client closed")
            except Exception as e:
                logger.warning("Error closing Weaviate client: %s", e)
            finally:
                _client = None
                _connected = False