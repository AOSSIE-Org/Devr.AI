"""
Enhanced Discord Client with Rate Limit Handling

This module provides a wrapper around discord.py client with automatic
rate limit handling and retry logic.
"""

import logging
from typing import Optional, Union, Dict, Any
import discord
from discord.ext import commands

from rate_limiter import get_rate_limiter, DiscordRateLimiter

logger = logging.getLogger(__name__)


class EnhancedDiscordClient:
    """
    Enhanced Discord client with built-in rate limit handling.
    
    Provides methods for sending and editing messages with automatic
    retry logic on rate limit errors.
    """

    def __init__(
        self,
        bot: Union[commands.Bot, discord.Client],
        rate_limiter: Optional[DiscordRateLimiter] = None,
    ):
        """
        Initialize the enhanced Discord client.

        Args:
            bot: The discord.py bot or client instance
            rate_limiter: Optional custom rate limiter instance
        """
        self.bot = bot
        self.rate_limiter = rate_limiter or get_rate_limiter()

    async def send_message_with_retry(
        self,
        channel: Union[discord.TextChannel, discord.DMChannel, int],
        content: Optional[str] = None,
        *,
        embed: Optional[discord.Embed] = None,
        embeds: Optional[list] = None,
        file: Optional[discord.File] = None,
        files: Optional[list] = None,
        delete_after: Optional[float] = None,
        nonce: Optional[Union[str, int]] = None,
        allowed_mentions: Optional[discord.AllowedMentions] = None,
        reference: Optional[Union[discord.Message, discord.MessageReference]] = None,
        mention_author: Optional[bool] = None,
        view: Optional[discord.ui.View] = None,
        poll: Optional[discord.Poll] = None,
    ) -> discord.Message:
        """
        Send a message with automatic rate limit handling.

        Args:
            channel: The Discord channel to send to
            content: Message content
            embed: Single embed to attach
            embeds: List of embeds
            file: Single file attachment
            files: Multiple file attachments
            delete_after: Delete message after this many seconds
            nonce: Unique nonce for message
            allowed_mentions: Allowed mentions configuration
            reference: Message to reply to
            mention_author: Whether to mention author in reply
            view: UI View for buttons/select menus
            poll: Poll to attach

        Returns:
            The sent discord.Message

        Raises:
            discord.DiscordException: If all retries are exhausted
        """
        endpoint = "channels.messages.post"

        async def _send() -> discord.Message:
            # Convert channel ID to channel object if needed
            if isinstance(channel, int):
                ch = self.bot.get_channel(channel)
                if not ch:
                    ch = await self.bot.fetch_channel(channel)
            else:
                ch = channel

            return await ch.send(
                content=content,
                embed=embed,
                embeds=embeds,
                file=file,
                files=files,
                delete_after=delete_after,
                nonce=nonce,
                allowed_mentions=allowed_mentions,
                reference=reference,
                mention_author=mention_author,
                view=view,
                poll=poll,
            )

        try:
            message = await self.rate_limiter.execute_with_retry(
                _send,
                endpoint,
            )
            logger.debug(f"Message sent to channel {channel}")
            return message

        except Exception as e:
            logger.error(f"Failed to send message to {channel}: {e}")
            raise

    async def edit_message_with_retry(
        self,
        message: discord.Message,
        *,
        content: Optional[str] = None,
        embed: Optional[discord.Embed] = None,
        embeds: Optional[list] = None,
        file: Optional[discord.File] = None,
        files: Optional[list] = None,
        delete_after: Optional[float] = None,
        allowed_mentions: Optional[discord.AllowedMentions] = None,
        view: Optional[discord.ui.View] = None,
    ) -> discord.Message:
        """
        Edit a message with automatic rate limit handling.

        Args:
            message: The message to edit
            content: New message content
            embed: New embed
            embeds: New embeds list
            file: File to attach
            files: Files to attach
            delete_after: Delete after this many seconds
            allowed_mentions: Allowed mentions configuration
            view: New UI View

        Returns:
            The edited discord.Message

        Raises:
            discord.DiscordException: If all retries are exhausted
        """
        endpoint = "channels.messages.patch"

        async def _edit() -> discord.Message:
            return await message.edit(
                content=content,
                embed=embed,
                embeds=embeds,
                file=file,
                files=files,
                delete_after=delete_after,
                allowed_mentions=allowed_mentions,
                view=view,
            )

        try:
            edited = await self.rate_limiter.execute_with_retry(
                _edit,
                endpoint,
            )
            logger.debug(f"Message {message.id} edited")
            return edited

        except Exception as e:
            logger.error(f"Failed to edit message {message.id}: {e}")
            raise

    async def delete_message_with_retry(
        self,
        message: discord.Message,
        *,
        delay: Optional[float] = None,
    ) -> None:
        """
        Delete a message with automatic rate limit handling.

        Args:
            message: The message to delete
            delay: Delay in seconds before deletion

        Raises:
            discord.DiscordException: If all retries are exhausted
        """
        endpoint = "channels.messages.delete"

        async def _delete() -> None:
            await message.delete(delay=delay)

        try:
            await self.rate_limiter.execute_with_retry(
                _delete,
                endpoint,
            )
            logger.debug(f"Message {message.id} deleted")

        except Exception as e:
            logger.error(f"Failed to delete message {message.id}: {e}")
            raise

    async def add_reaction_with_retry(
        self,
        message: discord.Message,
        emoji: Union[str, discord.Emoji],
    ) -> None:
        """
        Add a reaction with automatic rate limit handling.

        Args:
            message: The message to react to
            emoji: The emoji to add

        Raises:
            discord.DiscordException: If all retries are exhausted
        """
        endpoint = "channels.messages.reactions.put"

        async def _add_reaction() -> None:
            await message.add_reaction(emoji)

        try:
            await self.rate_limiter.execute_with_retry(
                _add_reaction,
                endpoint,
            )
            logger.debug(f"Reaction added to message {message.id}")

        except Exception as e:
            logger.error(f"Failed to add reaction to message {message.id}: {e}")
            raise

    async def create_thread_with_retry(
        self,
        channel: discord.TextChannel,
        *,
        name: str,
        message: Optional[discord.Message] = None,
        auto_archive_duration: int = 60,
        type: Optional[discord.ChannelType] = None,
        slowmode_delay: Optional[int] = None,
    ) -> discord.Thread:
        """
        Create a thread with automatic rate limit handling.

        Args:
            channel: The channel to create thread in
            name: Thread name
            message: Message to create thread from (optional)
            auto_archive_duration: Archive duration in minutes
            type: Channel type
            slowmode_delay: Slowmode delay

        Returns:
            The created discord.Thread

        Raises:
            discord.DiscordException: If all retries are exhausted
        """
        endpoint = "channels.threads.create"

        async def _create_thread() -> discord.Thread:
            if message:
                return await message.create_thread(
                    name=name,
                    auto_archive_duration=auto_archive_duration,
                    slowmode_delay=slowmode_delay,
                )
            else:
                return await channel.create_thread(
                    name=name,
                    auto_archive_duration=auto_archive_duration,
                    type=type,
                    slowmode_delay=slowmode_delay,
                )

        try:
            thread = await self.rate_limiter.execute_with_retry(
                _create_thread,
                endpoint,
            )
            logger.debug(f"Thread '{name}' created in {channel.id}")
            return thread

        except Exception as e:
            logger.error(f"Failed to create thread '{name}': {e}")
            raise

    def get_rate_limit_status(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the current rate limit status.

        Args:
            endpoint: Specific endpoint to check (optional)

        Returns:
            Status dictionary
        """
        return self.rate_limiter.get_status(endpoint)

    def reset_rate_limits(self) -> None:
        """Reset all rate limit buckets."""
        self.rate_limiter.reset_all()


def create_enhanced_client(
    bot: Union[commands.Bot, discord.Client],
    rate_limiter: Optional[DiscordRateLimiter] = None,
) -> EnhancedDiscordClient:
    """
    Create an enhanced Discord client wrapper.

    Args:
        bot: The discord.py bot instance
        rate_limiter: Optional custom rate limiter

    Returns:
        EnhancedDiscordClient instance
    """
    return EnhancedDiscordClient(bot, rate_limiter)
