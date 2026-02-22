import pytest
import asyncio
import time
import discord
from unittest.mock import AsyncMock, MagicMock

from backend.rate_limiter import DiscordRateLimiter


class Mock429(discord.HTTPException):
    def __init__(self):
        response = MagicMock()
        response.status = 429
        super().__init__(response=response, message="Rate limit")
        self.status = 429
        self.retry_after = 0.1


@pytest.mark.asyncio
async def test_success_without_rate_limit():
    limiter = DiscordRateLimiter(redis_url=None)
    mock_func = AsyncMock(return_value="OK")

    result = await limiter.execute_with_retry(mock_func, "test_bucket")

    assert result == "OK"
    mock_func.assert_awaited_once()


@pytest.mark.asyncio
async def test_retry_on_429():
    limiter = DiscordRateLimiter(redis_url=None)

    mock_func = AsyncMock(side_effect=[Mock429(), "Success"])

    result = await limiter.execute_with_retry(mock_func, "bucket1")

    assert result == "Success"
    assert mock_func.await_count == 2


@pytest.mark.asyncio
async def test_max_retries_exceeded():
    limiter = DiscordRateLimiter(redis_url=None, max_retries=2)

    mock_func = AsyncMock(side_effect=Mock429())

    with pytest.raises(Exception):
        await limiter.execute_with_retry(mock_func, "bucket2")


@pytest.mark.asyncio
async def test_backoff_calculation():
    limiter = DiscordRateLimiter(redis_url=None)

    delay1 = limiter._calculate_backoff(0, 1)
    delay2 = limiter._calculate_backoff(1, 1)

    assert delay2 > delay1


@pytest.mark.asyncio
async def test_redis_key_set_on_429(monkeypatch):
    limiter = DiscordRateLimiter(redis_url=None)

    limiter.redis = AsyncMock()

    mock_func = AsyncMock(side_effect=[Mock429(), "OK"])

    await limiter.execute_with_retry(mock_func, "bucketX")

    limiter.redis.set.assert_called()


@pytest.mark.asyncio
async def test_wait_if_limited(monkeypatch):
    limiter = DiscordRateLimiter(redis_url=None)
    limiter.redis = AsyncMock()

    future_time = time.time() + 0.2
    limiter.redis.get.return_value = str(future_time)

    start = time.time()
    await limiter._wait_if_limited("bucketY")
    end = time.time()

    assert end - start >= 0.2