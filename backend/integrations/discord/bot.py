import discord
from discord.ext import commands
import logging
import os
import asyncio
from typing import Dict, Optional

from backend.rate_limiter import DiscordRateLimiter
from app.agents.devrel.github.github_toolkit import GitHubToolkit

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """
    DEV MODE Discord Bot
    Direct GitHubToolkit execution
    Per-channel rate limiting + simple queue (Lock-based)
    """

    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        intents.dm_messages = True

        super().__init__(
            command_prefix=None,
            intents=intents,
            heartbeat_timeout=60.0,
            **kwargs
        )

        self.active_threads: Dict[str, str] = {}
        self.channel_locks: Dict[str, asyncio.Lock] = {}

        # Redis-enabled per-channel rate limiter
        self.rate_limiter = DiscordRateLimiter(
            redis_url=os.getenv("REDIS_URL"),
            max_retries=3
        )

    def _get_channel_lock(self, channel_id: str) -> asyncio.Lock:
        if channel_id not in self.channel_locks:
            self.channel_locks[channel_id] = asyncio.Lock()
        return self.channel_locks[channel_id]

    async def on_ready(self):
        logger.info(f'Bot logged in as {self.user}')
        print(f'Bot is ready! Logged in as {self.user}')

        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"Failed to sync slash commands: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.interaction_metadata is not None:
            return

        try:
            user_id = str(message.author.id)
            thread_id = await self._get_or_create_thread(message, user_id)
            thread = self.get_channel(int(thread_id))

            if not thread:
                return

            channel_id = str(thread.id)
            lock = self._get_channel_lock(channel_id)

            async with lock:

                # Send processing message
                await self.rate_limiter.execute_with_retry(
                    thread.send,
                    channel_id,
                    "Processing your request..."
                )

                # Execute toolkit
                toolkit = GitHubToolkit()
                result = await toolkit.execute(message.content)
                response_text = result.get("message", "No response generated.")

                # Send response in chunks
                for i in range(0, len(response_text), 2000):
                    await self.rate_limiter.execute_with_retry(
                        thread.send,
                        channel_id,
                        response_text[i:i+2000]
                    )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    async def _get_or_create_thread(self, message, user_id: str) -> Optional[str]:
        try:
            if user_id in self.active_threads:
                thread_id = self.active_threads[user_id]
                thread = self.get_channel(int(thread_id))
                if thread and not thread.archived:
                    return thread_id
                else:
                    del self.active_threads[user_id]

            if isinstance(message.channel, discord.TextChannel):
                thread_name = f"DevRel Chat - {message.author.display_name}"
                thread = await message.create_thread(
                    name=thread_name,
                    auto_archive_duration=60
                )

                self.active_threads[user_id] = str(thread.id)

                channel_id = str(thread.id)
                lock = self._get_channel_lock(channel_id)

                async with lock:
                    await self.rate_limiter.execute_with_retry(
                        thread.send,
                        channel_id,
                        f"Hello {message.author.mention}! "
                        "I've created this thread to help you."
                    )

                return str(thread.id)

        except Exception as e:
            logger.error(f"Failed to create thread: {e}")

        return str(message.channel.id)