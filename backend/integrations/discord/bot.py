import discord
from discord.ext import commands
import logging
from typing import Dict, Optional

from app.agents.devrel.github.github_toolkit import GitHubToolkit

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """
    DEV MODE Discord Bot
    Direct GitHubToolkit execution
    No Queue, No Agent, No Gemini
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
            if thread:
                await thread.send("Processing your request...")

            # 🔥 Direct Toolkit Execution
            toolkit = GitHubToolkit()
            result = await toolkit.execute(message.content)

            response_text = result.get("message", "No response generated.")

            if thread:
                for i in range(0, len(response_text), 2000):
                    await thread.send(response_text[i:i+2000])

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    async def _get_or_create_thread(
        self,
        message,
        user_id: str
    ) -> Optional[str]:

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
                await thread.send(
                    f"Hello {message.author.mention}! "
                    "I've created this thread to help you."
                )
                return str(thread.id)

        except Exception as e:
            logger.error(f"Failed to create thread: {e}")

        return str(message.channel.id)