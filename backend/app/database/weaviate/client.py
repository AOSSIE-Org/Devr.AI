import weaviate
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """Get or create the global Weaviate client instance."""
    global _client
    if _client is None:
        _client = weaviate.connect_to_local()
    return _client

@asynccontextmanager
async def get_weaviate_client() -> AsyncGenerator[weaviate.WeaviateClient, None]:
    """Async context manager for Weaviate client."""
    client = get_client()
    try:
        yield client
    except Exception as e:
        logger.error(f"Weaviate client error: {str(e)}")
        raise
    finally:
        try:
            client.close()
        except Exception as e:
            logger.warning(f"Error closing Weaviate client: {str(e)}")
