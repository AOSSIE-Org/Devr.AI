import asyncio
import random
import logging
import time
import discord
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class DiscordRateLimiter:
    def __init__(self, redis_url: str = None, max_retries: int = 3):
        self.max_retries = max_retries
        self.redis = redis.from_url(redis_url) if redis_url else None

    def _calculate_backoff(self, attempt: int, retry_after: float) -> float:
        backoff = (2 ** attempt) * retry_after
        jitter = random.uniform(0, 0.3)
        return backoff + jitter

    async def _wait_if_limited(self, bucket: str):
        if not self.redis:
            return

        key = f"discord_ratelimit:{bucket}"
        reset_time = await self.redis.get(key)

        if reset_time:
            delay = float(reset_time) - time.time()
            if delay > 0:
                logger.warning(
                    f"Bucket {bucket} rate limited. Waiting {delay:.2f}s"
                )
                await asyncio.sleep(delay)

    async def _set_limit(self, bucket: str, retry_after: float):
        if not self.redis:
            return

        key = f"discord_ratelimit:{bucket}"
        reset_at = time.time() + retry_after

        await self.redis.set(
            key,
            reset_at,
            ex=int(retry_after) + 1
        )

    async def execute_with_retry(self, func, bucket: str, *args, **kwargs):
        attempt = 0

        while attempt <= self.max_retries:
            try:
                await self._wait_if_limited(bucket)
                return await func(*args, **kwargs)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = getattr(e, "retry_after", 1)

                    await self._set_limit(bucket, retry_after)

                    delay = self._calculate_backoff(attempt, retry_after)

                    logger.warning(
                        f"429 hit for bucket {bucket}. "
                        f"Attempt {attempt + 1}. "
                        f"Retrying in {delay:.2f}s"
                    )

                    await asyncio.sleep(delay)
                    attempt += 1
                else:
                    raise

        logger.error(f"Max retries exhausted for bucket {bucket}")
        raise Exception("Discord rate limit exceeded after retries.")