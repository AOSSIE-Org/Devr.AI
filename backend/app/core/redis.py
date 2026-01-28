import redis.asyncio as redis
import asyncio
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RedisClient:
    _instance: Optional[redis.Redis] = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    # Mask credentials for logging
                    log_url = settings.redis_url
                    if "@" in log_url:
                        try:
                            schema, rest = log_url.split("://", 1)
                            auth, host = rest.split("@", 1)
                            log_url = f"{schema}://****:****@{host}"
                        except Exception:
                            log_url = "redis://****:****@..."

                    logger.info(f"Initializing Redis client connecting to {log_url}")
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

async def get_redis_client() -> redis.Redis:
    """Dependency to get the Redis client instance."""
    return await RedisClient.get_client()
