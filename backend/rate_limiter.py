"""
Discord Rate Limiter with Exponential Backoff Retry Mechanism

This module provides robust rate limit handling for Discord API interactions,
including exponential backoff retry logic and per-endpoint tracking.
"""

import asyncio
import time
import logging
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


@dataclass
class RateLimitBucket:
    """Represents a rate limit bucket for a Discord endpoint."""
    name: str
    remaining: int = 1
    reset_at: float = field(default_factory=time.time)
    retry_after: Optional[float] = None
    last_reset: float = field(default_factory=time.time)

    def is_rate_limited(self) -> bool:
        """Check if bucket is currently rate limited."""
        if self.remaining > 0:
            return False
        if self.reset_at <= time.time():
            self.reset()
            return False
        return True

    def reset(self) -> None:
        """Reset the rate limit bucket."""
        self.remaining = 1
        self.reset_at = time.time()
        self.retry_after = None
        self.last_reset = time.time()

    def wait_time(self) -> float:
        """Get seconds to wait before bucket is available."""
        if not self.is_rate_limited():
            return 0
        return max(0, self.reset_at - time.time())


class DiscordRateLimiter:
    """
    Manages Discord API rate limiting with exponential backoff retry logic.
    
    Features:
    - Per-endpoint rate limit tracking
    - Exponential backoff with jitter
    - Configurable retry attempts
    - Comprehensive logging
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        """
        Initialize the rate limiter.

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay for exponential backoff in seconds (default: 1.0)
            max_delay: Maximum delay cap in seconds (default: 60.0)
            jitter: Whether to add random jitter to delays (default: True)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.buckets: Dict[str, RateLimitBucket] = {}
        self.request_queue: Optional[asyncio.Queue] = None
        self.processor_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize async components."""
        self.request_queue = asyncio.Queue()
        self.processor_task = asyncio.create_task(self._process_queue())
        logger.info("Rate limiter initialized")

    async def shutdown(self) -> None:
        """Shutdown and cleanup."""
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Rate limiter shutdown")

    def _get_bucket(self, endpoint: str) -> RateLimitBucket:
        """Get or create a rate limit bucket for an endpoint."""
        if endpoint not in self.buckets:
            self.buckets[endpoint] = RateLimitBucket(name=endpoint)
        return self.buckets[endpoint]

    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with optional jitter.

        Formula: min(base_delay * (2 ^ attempt) + jitter, max_delay)

        Args:
            attempt: The retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (2 ** attempt)

        if self.jitter:
            # Add random jitter: ±10% of delay
            jitter_amount = delay * 0.1 * random.random()
            delay += jitter_amount if random.random() > 0.5 else -jitter_amount

        return min(delay, self.max_delay)

    async def wait_if_rate_limited(self, endpoint: str) -> float:
        """
        Wait if the endpoint is rate limited.

        Args:
            endpoint: The Discord API endpoint

        Returns:
            Actual wait time in seconds
        """
        bucket = self._get_bucket(endpoint)

        if bucket.is_rate_limited():
            wait_time = bucket.wait_time()
            logger.warning(
                f"Rate limit detected for {endpoint}, waiting {wait_time:.2f}s"
            )
            await asyncio.sleep(wait_time)
            bucket.reset()
            return wait_time

        return 0

    async def execute_with_retry(
        self,
        func: Callable,
        endpoint: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a function with automatic retry on rate limits.

        Args:
            func: The async function to execute
            endpoint: The Discord API endpoint identifier
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            The result of the function call

        Raises:
            Exception: If all retries are exhausted
        """
        bucket = self._get_bucket(endpoint)
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Check rate limit before executing
                await self.wait_if_rate_limited(endpoint)

                # Execute the function
                result = await func(*args, **kwargs)

                if attempt > 0:
                    logger.info(
                        f"Successful retry for {endpoint} on attempt {attempt + 1}"
                    )

                return result

            except Exception as e:
                last_error = e
                error_name = type(e).__name__

                # Check if it's a rate limit error (429)
                is_rate_limit_error = (
                    hasattr(e, "status") and e.status == 429
                ) or (
                    "429" in str(e) or "rate_limit" in str(e).lower()
                )

                if is_rate_limit_error:
                    # Extract retry_after if available
                    retry_after = None
                    if hasattr(e, "retry_after"):
                        retry_after = e.retry_after

                    if retry_after:
                        bucket.retry_after = retry_after
                        bucket.reset_at = time.time() + retry_after

                    if attempt < self.max_retries:
                        wait_time = self._calculate_backoff(attempt)
                        logger.warning(
                            f"Rate limit error for {endpoint} (attempt {attempt + 1}/{self.max_retries + 1}), "
                            f"retrying in {wait_time:.2f}s"
                        )
                        await asyncio.sleep(wait_time)
                        continue

                    logger.error(
                        f"Rate limit error for {endpoint} - max retries ({self.max_retries}) exhausted"
                    )
                    raise

                # For non-rate-limit errors, raise immediately
                logger.error(
                    f"Error executing {endpoint}: {error_name} - {str(e)}"
                )
                raise

        if last_error:
            raise last_error

    async def _process_queue(self) -> None:
        """Process queued requests."""
        while True:
            try:
                await asyncio.sleep(0.1)
                # Queue processing logic for future use
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")

    def get_status(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get rate limiter status.

        Args:
            endpoint: Specific endpoint to check, or None for all

        Returns:
            Status dictionary
        """
        if endpoint:
            if endpoint not in self.buckets:
                return {"endpoint": endpoint, "status": "no_data"}

            bucket = self.buckets[endpoint]
            return {
                "endpoint": endpoint,
                "remaining": bucket.remaining,
                "reset_at": datetime.fromtimestamp(bucket.reset_at).isoformat(),
                "is_rate_limited": bucket.is_rate_limited(),
                "wait_time": bucket.wait_time(),
            }

        return {
            "total_buckets": len(self.buckets),
            "buckets": {
                name: {
                    "remaining": bucket.remaining,
                    "is_rate_limited": bucket.is_rate_limited(),
                    "wait_time": bucket.wait_time(),
                }
                for name, bucket in self.buckets.items()
            },
        }

    def reset_all(self) -> None:
        """Reset all rate limit buckets."""
        for bucket in self.buckets.values():
            bucket.reset()
        logger.info("All rate limit buckets reset")


# Global rate limiter instance
_rate_limiter: Optional[DiscordRateLimiter] = None


def get_rate_limiter() -> DiscordRateLimiter:
    """Get or create the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = DiscordRateLimiter()
    return _rate_limiter


async def initialize_rate_limiter() -> DiscordRateLimiter:
    """Initialize the global rate limiter."""
    limiter = get_rate_limiter()
    await limiter.initialize()
    return limiter


async def shutdown_rate_limiter() -> None:
    """Shutdown the global rate limiter."""
    global _rate_limiter
    if _rate_limiter:
        await _rate_limiter.shutdown()
        _rate_limiter = None
