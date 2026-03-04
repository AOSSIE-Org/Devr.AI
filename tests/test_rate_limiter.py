"""
Unit tests for Discord rate limiter.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from rate_limiter import (
    DiscordRateLimiter,
    RateLimitBucket,
    get_rate_limiter,
    initialize_rate_limiter,
    shutdown_rate_limiter,
)


class TestRateLimitBucket:
    """Test RateLimitBucket functionality."""

    def test_bucket_initialization(self):
        """Test bucket initializes with correct values."""
        bucket = RateLimitBucket(name="test_endpoint")
        assert bucket.name == "test_endpoint"
        assert bucket.remaining > 0
        assert not bucket.is_rate_limited()

    def test_bucket_is_rate_limited(self):
        """Test rate limited detection."""
        bucket = RateLimitBucket(name="test")
        assert not bucket.is_rate_limited()

        bucket.remaining = 0
        bucket.reset_at = time.time() + 10
        assert bucket.is_rate_limited()

    def test_bucket_reset(self):
        """Test bucket reset."""
        bucket = RateLimitBucket(name="test")
        bucket.remaining = 0
        bucket.reset_at = time.time() + 100
        bucket.retry_after = 50

        bucket.reset()

        assert bucket.remaining > 0
        assert bucket.retry_after is None

    def test_bucket_wait_time(self):
        """Test wait time calculation."""
        bucket = RateLimitBucket(name="test")
        bucket.remaining = 0
        bucket.reset_at = time.time() + 5

        wait = bucket.wait_time()
        assert 4.9 < wait <= 5.0


class TestDiscordRateLimiter:
    """Test DiscordRateLimiter functionality."""

    @pytest.fixture
    def limiter(self):
        """Create a rate limiter instance."""
        return DiscordRateLimiter(max_retries=3, base_delay=0.1)

    def test_limiter_initialization(self, limiter):
        """Test limiter initializes correctly."""
        assert limiter.max_retries == 3
        assert limiter.base_delay == 0.1
        assert len(limiter.buckets) == 0

    def test_get_bucket(self, limiter):
        """Test bucket creation and retrieval."""
        bucket1 = limiter._get_bucket("endpoint1")
        bucket2 = limiter._get_bucket("endpoint1")

        assert bucket1 is bucket2
        assert bucket1.name == "endpoint1"

    def test_calculate_backoff_exponential(self, limiter):
        """Test exponential backoff calculation."""
        limiter.jitter = False  # Disable jitter for predictable values

        # 2^0 * 0.1 = 0.1
        assert limiter._calculate_backoff(0) == 0.1

        # 2^1 * 0.1 = 0.2
        assert limiter._calculate_backoff(1) == 0.2

        # 2^2 * 0.1 = 0.4
        assert limiter._calculate_backoff(2) == 0.4

        # 2^10 * 0.1 = 102.4, capped at 60
        assert limiter._calculate_backoff(10) == 60.0

    def test_calculate_backoff_with_jitter(self, limiter):
        """Test backoff with jitter adds variance."""
        limiter.jitter = True

        delays = [limiter._calculate_backoff(1) for _ in range(10)]

        # With jitter, we should get different values
        assert len(set(delays)) > 1

        # All should be within reasonable bounds
        for delay in delays:
            assert 0.15 < delay < 0.25

    def test_calculate_backoff_max_cap(self, limiter):
        """Test max delay cap."""
        limiter.jitter = False

        # Very large attempt should be capped
        assert limiter._calculate_backoff(100) == 60.0

    @pytest.mark.asyncio
    async def test_wait_if_rate_limited_not_limited(self, limiter):
        """Test wait when not rate limited."""
        await limiter.initialize()

        wait = await limiter.wait_if_rate_limited("endpoint")
        assert wait == 0

        await limiter.shutdown()

    @pytest.mark.asyncio
    async def test_wait_if_rate_limited_is_limited(self, limiter):
        """Test wait when rate limited."""
        await limiter.initialize()

        bucket = limiter._get_bucket("endpoint")
        bucket.remaining = 0
        bucket.reset_at = time.time() + 0.2

        start = time.time()
        wait = await limiter.wait_if_rate_limited("endpoint")
        elapsed = time.time() - start

        assert elapsed >= 0.18
        assert wait == pytest.approx(0.2, abs=0.03)
        assert not bucket.is_rate_limited()

        await limiter.shutdown()

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self, limiter):
        """Test successful execution."""
        await limiter.initialize()

        async_func = AsyncMock(return_value="success")

        result = await limiter.execute_with_retry(async_func, "endpoint")

        assert result == "success"
        assert async_func.call_count == 1

        await limiter.shutdown()

    @pytest.mark.asyncio
    async def test_execute_with_retry_non_rate_limit_error(self, limiter):
        """Test non-rate-limit error raises immediately."""
        await limiter.initialize()

        async_func = AsyncMock(side_effect=ValueError("Bad input"))

        with pytest.raises(ValueError):
            await limiter.execute_with_retry(async_func, "endpoint")

        assert async_func.call_count == 1

        await limiter.shutdown()

    @pytest.mark.asyncio
    async def test_execute_with_retry_rate_limit_retry(self, limiter):
        """Test rate limit error triggers retry."""
        await limiter.initialize()

        error = Exception("429 rate limit")
        async_func = AsyncMock(
            side_effect=[error, error, "success"]
        )

        result = await limiter.execute_with_retry(async_func, "endpoint")

        assert result == "success"
        assert async_func.call_count == 3

        await limiter.shutdown()

    @pytest.mark.asyncio
    async def test_execute_with_retry_exhausted(self, limiter):
        """Test retry exhaustion."""
        await limiter.initialize()

        error = Exception("429 rate limit")
        async_func = AsyncMock(side_effect=error)

        with pytest.raises(Exception):
            await limiter.execute_with_retry(async_func, "endpoint")

        # max_retries=3, plus initial attempt = 4 calls
        assert async_func.call_count == 4

        await limiter.shutdown()

    def test_get_status_no_data(self, limiter):
        """Test status for unknown endpoint."""
        status = limiter.get_status("unknown")
        assert status["endpoint"] == "unknown"
        assert status["status"] == "no_data"

    def test_get_status_specific_endpoint(self, limiter):
        """Test status for specific endpoint."""
        limiter._get_bucket("endpoint")

        status = limiter.get_status("endpoint")

        assert status["endpoint"] == "endpoint"
        assert "remaining" in status
        assert "reset_at" in status
        assert "is_rate_limited" in status

    def test_get_status_all_endpoints(self, limiter):
        """Test status for all endpoints."""
        limiter._get_bucket("endpoint1")
        limiter._get_bucket("endpoint2")

        status = limiter.get_status()

        assert status["total_buckets"] == 2
        assert "endpoint1" in status["buckets"]
        assert "endpoint2" in status["buckets"]

    def test_reset_all(self, limiter):
        """Test reset all buckets."""
        bucket1 = limiter._get_bucket("endpoint1")
        bucket2 = limiter._get_bucket("endpoint2")

        bucket1.remaining = 0
        bucket2.remaining = 0

        limiter.reset_all()

        assert bucket1.remaining > 0
        assert bucket2.remaining > 0

    @pytest.mark.asyncio
    async def test_initialize_shutdown(self):
        """Test initialize and shutdown."""
        limiter = DiscordRateLimiter()

        await limiter.initialize()
        assert limiter.request_queue is not None
        assert limiter.processor_task is not None

        await limiter.shutdown()

    def test_global_rate_limiter(self):
        """Test global rate limiter instance."""
        import rate_limiter as rl_module
        original = rl_module._rate_limiter
        try:
            rl_module._rate_limiter = None
            limiter1 = get_rate_limiter()
            limiter2 = get_rate_limiter()
            assert limiter1 is limiter2
        finally:
            rl_module._rate_limiter = original


class TestBackoffCalculation:
    """Test backoff calculation edge cases."""

    @pytest.fixture
    def limiter(self):
        """Create limiter for testing."""
        return DiscordRateLimiter(base_delay=1.0, jitter=False)

    def test_exponential_sequence(self, limiter):
        """Test exponential backoff sequence."""
        expected = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 60.0, 60.0]

        for i, exp in enumerate(expected):
            assert limiter._calculate_backoff(i) == exp

    def test_jitter_bounds(self):
        """Test jitter stays within bounds."""
        limiter = DiscordRateLimiter(base_delay=1.0, max_delay=10.0, jitter=True)

        for _ in range(100):
            delay = limiter._calculate_backoff(2)
            assert 0 < delay <= 10.0
