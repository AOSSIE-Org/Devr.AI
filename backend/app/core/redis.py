import redis.asyncio as redis
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RedisClient:
    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            logger.info(f"Initializing Redis client connecting to {settings.redis_url}")
            cls._instance = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
            logger.info("Redis client closed.")

def get_redis_client() -> redis.Redis:
    """Dependency to get the Redis client instance."""
    return RedisClient.get_client()
