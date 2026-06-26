import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import discord
import aiohttp

from integrations.discord.retry import (
    calculate_backoff,
    discord_retry,
    get_discord_retry_after,
    is_retriable_exception,
    run_with_retry,
)


def test_get_discord_retry_after_from_attribute():
    """Test extracting retry_after from an exception attribute (like RateLimited)."""
    exc = Exception("Rate limited")
    exc.retry_after = 2.5
    assert get_discord_retry_after(exc) == 2.5


def test_get_discord_retry_after_from_headers():
    """Test extracting retry_after from HTTPException response headers."""
    # Mock response and headers
    response = MagicMock(spec=aiohttp.ClientResponse)
    response.headers = {
        "X-RateLimit-Reset-After": "1.75",
        "Retry-After": "3.0",
    }

    # HTTPException mock
    exc = discord.HTTPException(response, "Too Many Requests")
    assert get_discord_retry_after(exc) == 1.75


def test_get_discord_retry_after_from_retry_after_header():
    """Test extracting retry_after when only Retry-After header is present."""
    response = MagicMock(spec=aiohttp.ClientResponse)
    response.headers = {
        "Retry-After": "4.2",
    }

    exc = discord.HTTPException(response, "Too Many Requests")
    assert get_discord_retry_after(exc) == 4.2


def test_get_discord_retry_after_from_json_body():
    """Test extracting retry_after from the exception text body."""
    response = MagicMock(spec=aiohttp.ClientResponse)
    response.headers = {}

    exc = discord.HTTPException(response, "Too Many Requests")
    exc.text = json.dumps({"retry_after": 0.350})
    assert get_discord_retry_after(exc) == 0.350


def test_get_discord_retry_after_none():
    """Test that None is returned if no rate limit headers/attributes exist."""
    exc = ValueError("Some other error")
    assert get_discord_retry_after(exc) is None


def test_calculate_backoff():
    """Test calculation of exponential backoff with jitter."""
    for attempt in range(1, 4):
        delay = calculate_backoff(attempt, base_delay=1.0, max_delay=10.0)
        assert 0.1 <= delay <= 10.0


def test_is_retriable_exception():
    """Test logic for identifying transient/retriable errors."""
    # 1. DiscordServerError
    response = MagicMock(spec=aiohttp.ClientResponse)
    server_err = discord.DiscordServerError(response, "Internal Server Error")
    assert is_retriable_exception(server_err) is True

    # 2. HTTPException with 429
    response_429 = MagicMock(spec=aiohttp.ClientResponse)
    response_429.status = 429
    exc_429 = discord.HTTPException(response_429, "Too Many Requests")
    assert is_retriable_exception(exc_429) is True

    # 3. HTTPException with 502
    response_502 = MagicMock(spec=aiohttp.ClientResponse)
    response_502.status = 502
    exc_502 = discord.HTTPException(response_502, "Bad Gateway")
    assert is_retriable_exception(exc_502) is True

    # 4. HTTPException with 403 (Forbidden - NOT retriable)
    response_403 = MagicMock(spec=aiohttp.ClientResponse)
    response_403.status = 403
    exc_403 = discord.HTTPException(response_403, "Forbidden")
    assert is_retriable_exception(exc_403) is False

    # 5. ClientError and TimeoutError
    assert is_retriable_exception(aiohttp.ClientError("Network drop")) is True
    assert is_retriable_exception(asyncio.TimeoutError()) is True


@pytest.mark.asyncio
async def test_discord_retry_success_first_try():
    """Test decorator works directly when no exception occurs."""
    mock_func = AsyncMock(return_value="success")

    decorated = discord_retry(max_retries=3, base_delay=0.1)(mock_func)
    result = await decorated("arg1", kwarg1="val")

    assert result == "success"
    mock_func.assert_called_once_with("arg1", kwarg1="val")


@pytest.mark.asyncio
async def test_discord_retry_success_after_rate_limit():
    """Test decorator retries after hitting rate limit exception, parsing headers."""
    # Create mock exception with retry_after attribute
    rate_limit_exc = Exception("Rate limited")
    rate_limit_exc.retry_after = 0.05

    # Async function that fails first time then succeeds
    call_count = 0

    @discord_retry(max_retries=3, base_delay=0.1)
    async def sample_func():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise rate_limit_exc
        return "finally_success"

    with patch("asyncio.sleep") as mock_sleep:
        result = await sample_func()

        assert result == "finally_success"
        assert call_count == 2
        mock_sleep.assert_called_once()
        args, _ = mock_sleep.call_args
        assert args[0] == pytest.approx(0.15)


@pytest.mark.asyncio
async def test_discord_retry_success_after_transient_error():
    """Test decorator retries after hitting a transient 502 error."""
    response = MagicMock(spec=aiohttp.ClientResponse)
    response.status = 502
    transient_exc = discord.HTTPException(response, "Bad Gateway")

    call_count = 0

    @discord_retry(max_retries=3, base_delay=0.1)
    async def sample_func():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise transient_exc
        return "success"

    with patch("asyncio.sleep") as mock_sleep:
        result = await sample_func()

        assert result == "success"
        assert call_count == 2
        mock_sleep.assert_called_once()
        # Verify it slept some float value
        args, _ = mock_sleep.call_args
        assert args[0] > 0


@pytest.mark.asyncio
async def test_discord_retry_max_retries_exceeded():
    """Test decorator re-raises exception when max_retries limit is exceeded."""
    response = MagicMock(spec=aiohttp.ClientResponse)
    response.status = 502
    exc = discord.HTTPException(response, "Bad Gateway")

    @discord_retry(max_retries=2, base_delay=0.01)
    async def sample_func():
        raise exc

    with patch("asyncio.sleep") as mock_sleep:
        with pytest.raises(discord.HTTPException) as err:
            await sample_func()

        assert err.value.status == 502
        assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_run_with_retry_wrapper():
    """Test the run_with_retry function wrapper."""
    mock_func = AsyncMock(return_value="wrapper_success")

    result = await run_with_retry(mock_func, "arg", max_retries=2, base_delay=0.01)
    assert result == "wrapper_success"
    mock_func.assert_called_once_with("arg")
