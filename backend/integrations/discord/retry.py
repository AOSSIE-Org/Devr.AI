import asyncio
import logging
import random
import time
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

import aiohttp
import discord

logger = logging.getLogger(__name__)

T = TypeVar("T")


def get_discord_retry_after(exc: Exception) -> float | None:
    """
    Extracts the recommended retry-after delay (in seconds) from a Discord exception.

    Looks at:
      - The `retry_after` attribute of `discord.errors.RateLimited`.
      - HTTP response headers (X-RateLimit-Reset-After, Retry-After, X-RateLimit-Reset).
      - The JSON response body if present in the exception text.
    """
    # 1. Check if the exception has a direct retry_after attribute (e.g. discord.errors.RateLimited)
    if hasattr(exc, "retry_after"):
        try:
            return float(exc.retry_after)
        except (ValueError, TypeError):
            pass

    # 2. Check if it's an HTTPException with response headers or parsed data
    if isinstance(exc, discord.HTTPException):
        if hasattr(exc, "response") and exc.response is not None:
            headers = exc.response.headers

            # Check X-RateLimit-Reset-After (Discord specific, decimal seconds)
            reset_after = headers.get("X-RateLimit-Reset-After")
            if reset_after is not None:
                try:
                    return float(reset_after)
                except (ValueError, TypeError):
                    pass

            # Check standard HTTP Retry-After header
            retry_after = headers.get("Retry-After")
            if retry_after is not None:
                try:
                    return float(retry_after)
                except (ValueError, TypeError):
                    pass

            # Check X-RateLimit-Reset (epoch timestamp)
            reset_epoch = headers.get("X-RateLimit-Reset")
            if reset_epoch is not None:
                try:
                    delay = float(reset_epoch) - time.time()
                    if delay > 0:
                        return delay
                except (ValueError, TypeError):
                    pass

        # Try parsing from exception body text (JSON)
        if hasattr(exc, "text") and isinstance(exc.text, str):
            import json

            try:
                data = json.loads(exc.text)
                if isinstance(data, dict) and "retry_after" in data:
                    return float(data["retry_after"])
            except Exception:
                pass

    return None


def calculate_backoff(attempt: int, base_delay: float, max_delay: float) -> float:
    """
    Calculates exponential backoff delay with full jitter to avoid thundering herds.
    """
    temp = min(max_delay, base_delay * (2**attempt))
    return random.uniform(0.1, temp)


def is_retriable_exception(exc: Exception) -> bool:
    """
    Determines if an exception is transient and should be retried.

    Retriable exceptions:
      - Exceptions with a `retry_after` attribute (e.g. RateLimited)
      - discord.HTTPException with status 429 (Rate Limited) or 5xx (Server Error)
      - discord.DiscordServerError
      - aiohttp.ClientError (transient network issues)
      - asyncio.TimeoutError (request timeouts)
    """
    if hasattr(exc, "retry_after"):
        return True

    if isinstance(exc, discord.DiscordServerError):
        return True

    if isinstance(exc, discord.HTTPException):
        # 429 is Rate Limit, 5xx is server-side errors
        if exc.status == 429 or (exc.status is not None and exc.status >= 500):
            return True

    if isinstance(exc, (aiohttp.ClientError, asyncio.TimeoutError)):
        return True

    return False


def discord_retry(
    max_retries: int = 5,
    base_delay: float = 1.5,
    max_delay: float = 60.0,
):
    """
    Decorator that applies exponential backoff and Discord-aware rate-limit retries
    to asynchronous functions/methods making Discord API requests.

    - If a rate limit (HTTP 429) is hit, it parses the retry-after value from Discord headers
      or exception details and sleeps for that exact duration.
      If no explicit rate limit duration is found, it uses exponential backoff.
    - If a 5xx or transient network error occurs, it applies exponential backoff with full jitter.
    - If max_retries is reached, the last exception is re-raised.
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if not is_retriable_exception(exc):
                        raise exc

                    attempt += 1
                    if attempt > max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) reached for Discord API call {func.__name__}. Re-raising exception: {exc}"
                        )
                        raise exc

                    # Check for explicit Discord rate-limit sleep instruction
                    retry_after = get_discord_retry_after(exc)
                    if retry_after is not None:
                        sleep_time = retry_after
                        # Add a tiny buffer to avoid edge-case 429 loops (e.g. 100ms)
                        sleep_time += 0.1
                        logger.warning(
                            f"Discord API Rate Limited (429) in {func.__name__}. "
                            f"Respecting header: sleeping for {sleep_time:.3f}s. "
                            f"Attempt {attempt}/{max_retries}."
                        )
                    else:
                        sleep_time = calculate_backoff(attempt, base_delay, max_delay)
                        logger.warning(
                            f"Transient error ({type(exc).__name__}: {exc}) in {func.__name__}. "
                            f"Applying exponential backoff: sleeping for {sleep_time:.3f}s. "
                            f"Attempt {attempt}/{max_retries}."
                        )

                    await asyncio.sleep(sleep_time)

        return wrapper

    return decorator


async def run_with_retry(
    coro_func: Callable[..., Coroutine[Any, Any, T]],
    *args: Any,
    max_retries: int = 5,
    base_delay: float = 1.5,
    max_delay: float = 60.0,
    **kwargs: Any,
) -> T:
    """
    Wrapper function that executes any arbitrary async callable making a Discord API request,
    applying exponential backoff and rate-limit handling.

    Example:
        await run_with_retry(thread.send, "Hello world!")
    """

    # We can reuse the decorated version of an anonymous wrapper function
    @discord_retry(max_retries=max_retries, base_delay=base_delay, max_delay=max_delay)
    async def _execute():
        return await coro_func(*args, **kwargs)

    return await _execute()
