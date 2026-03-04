"""
Utility helpers for Discord rate limiting and error handling.
"""

import logging
from typing import Optional, Union
import discord

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when a Discord rate limit is encountered."""

    def __init__(
        self,
        endpoint: str,
        retry_after: float,
        message: str = "Rate limited by Discord API",
    ):
        """
        Initialize RateLimitError.

        Args:
            endpoint: The Discord endpoint that was rate limited
            retry_after: Seconds to wait before retrying
            message: Error message
        """
        self.endpoint = endpoint
        self.retry_after = retry_after
        super().__init__(f"{message} ({endpoint}): retry after {retry_after}s")


class DiscordException(Exception):
    """Base exception for Discord client errors."""

    pass


def extract_retry_after(error: Exception) -> Optional[float]:
    """
    Extract retry_after value from Discord exception.

    Args:
        error: The exception to parse

    Returns:
        Retry after in seconds, or None if not found
    """
    if hasattr(error, "retry_after"):
        return error.retry_after

    if hasattr(error, "response"):
        headers = getattr(error.response, "headers", {})
        if "Retry-After" in headers:
            try:
                return float(headers["Retry-After"])
            except (ValueError, TypeError):
                pass

    # Check error message
    error_str = str(error).lower()
    if "retry-after" in error_str or "rate limit" in error_str:
        return None

    return None


def is_rate_limit_error(error: Exception) -> bool:
    """
    Check if an exception is a rate limit error.

    Args:
        error: The exception to check

    Returns:
        True if it's a rate limit error, False otherwise
    """
    # Check discord.py HTTPException
    if isinstance(error, discord.HTTPException):
        return error.status == 429

    # Check by status attribute
    if hasattr(error, "status"):
        return error.status == 429

    # Check error message
    error_str = str(error)
    return "429" in error_str or "rate" in error_str.lower()


def create_rate_limit_embed(
    endpoint: str,
    retry_after: float,
    attempt: int,
) -> discord.Embed:
    """
    Create an embed for rate limit notification.

    Args:
        endpoint: The rate limited endpoint
        retry_after: Seconds to wait
        attempt: The current attempt number

    Returns:
        discord.Embed for display
    """
    embed = discord.Embed(
        title="⏱️ Rate Limit Encountered",
        description=f"The Discord API is rate limiting requests to `{endpoint}`.",
        color=discord.Color.orange(),
    )

    embed.add_field(
        name="Retry After",
        value=f"{retry_after:.1f} seconds",
        inline=True,
    )

    embed.add_field(
        name="Attempt",
        value=f"{attempt}",
        inline=True,
    )

    embed.add_field(
        name="Status",
        value="Automatically retrying...",
        inline=False,
    )

    embed.set_footer(text="This is a temporary issue and will be resolved.")

    return embed


def create_error_embed(
    endpoint: str,
    error: Exception,
    attempt: int,
    max_attempts: int,
) -> discord.Embed:
    """
    Create an embed for error notification.

    Args:
        endpoint: The endpoint that failed
        error: The exception that occurred
        attempt: The current attempt number
        max_attempts: Maximum attempts allowed

    Returns:
        discord.Embed for display
    """
    embed = discord.Embed(
        title="❌ Operation Failed",
        description=f"Failed to complete request to `{endpoint}`.",
        color=discord.Color.red(),
    )

    embed.add_field(
        name="Error",
        value=f"```\n{type(error).__name__}\n```",
        inline=False,
    )

    embed.add_field(
        name="Attempts",
        value=f"{attempt}/{max_attempts}",
        inline=True,
    )

    embed.add_field(
        name="Message",
        value=str(error)[:100],
        inline=False,
    )

    embed.set_footer(text="Please try again later or contact support.")

    return embed


def format_retry_after(seconds: float) -> str:
    """
    Format retry_after value as human-readable string.

    Args:
        seconds: Seconds to wait

    Returns:
        Formatted string
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_user_friendly_error(error: Exception) -> str:
    """
    Get a user-friendly error message.

    Args:
        error: The exception

    Returns:
        User-friendly error message
    """
    if is_rate_limit_error(error):
        retry_after = extract_retry_after(error)
        if retry_after:
            return (
                f"Discord API is temporarily busy. "
                f"Please wait {format_retry_after(retry_after)} and try again."
            )
        return "Discord API is temporarily busy. Please wait a moment and try again."

    if isinstance(error, discord.Forbidden):
        return "I don't have permission to perform this action."

    if isinstance(error, discord.NotFound):
        return "The requested resource was not found."

    if isinstance(error, discord.HTTPException):
        return f"Discord API error: {error.status}"

    return f"An error occurred: {str(error)}"


class LoggingConfig:
    """Configuration for rate limiter logging."""

    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR

    @staticmethod
    def setup(
        name: str = "discord_rate_limiter",
        level: int = logging.INFO,
        format_string: Optional[str] = None,
    ) -> logging.Logger:
        """
        Setup logging for rate limiter.

        Args:
            name: Logger name
            level: Logging level
            format_string: Custom format string

        Returns:
            Configured logger
        """
        if format_string is None:
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        logger_obj = logging.getLogger(name)
        logger_obj.setLevel(level)

        # Console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)

        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        logger_obj.addHandler(handler)

        return logger_obj
