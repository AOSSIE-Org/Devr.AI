import weaviate
import weaviate.exceptions
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

def get_client():
    """Create a new async Weaviate client instance per context use."""
    return weaviate.use_async_with_local()

@asynccontextmanager
async def get_weaviate_client() -> AsyncGenerator[weaviate.WeaviateClient, None]:
    """Async context manager for Weaviate client."""
    client = get_client()
    try:
        await client.connect()
        yield client
    except weaviate.exceptions.WeaviateBaseError as e:
        logger.error("Weaviate client error: %s", e, exc_info=True)
        raise
    finally:
        try:
            await client.close()
        except Exception as e:
            logger.warning("Error closing Weaviate client: %s", e, exc_info=True)
