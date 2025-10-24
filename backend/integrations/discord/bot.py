import discord
from discord.ext import commands
import logging
from typing import Dict, Any, Optional
from app.core.orchestration.queue_manager import AsyncQueueManager, QueuePriority
from app.classification.classification_router import ClassificationRouter

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Discord bot with LangGraph agent integration"""

    def __init__(self, queue_manager: AsyncQueueManager, **kwargs):
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

        self.queue_manager = queue_manager
        self.classifier = ClassificationRouter()
        self.active_threads: Dict[str, str] = {}
        self._register_queue_handlers()

    def _register_queue_handlers(self):
        """Register handlers for queue messages"""
        self.queue_manager.register_handler("discord_response", self._handle_agent_response)

    async def on_ready(self):
        """Bot ready event"""
        logger.info(f'Enhanced Discord bot logged in as {self.user}')
        print(f'Bot is ready! Logged in as {self.user}')
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"Failed to sync slash commands: {e}")

    async def on_message(self, message):
        """Handles regular chat messages, but ignores slash commands."""
        if message.author == self.user:
            return

        if message.interaction_metadata is not None:
            return

        try:
            triage_result = await self.classifier.should_process_message(
                message.content,
                {
                    "channel_id": str(message.channel.id),
                    "user_id": str(message.author.id),
                    "guild_id": str(message.guild.id) if message.guild else None
                }
            )

            if triage_result.get("needs_devrel", False):
                await self._handle_devrel_message(message, triage_result)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    async def _handle_devrel_message(self, message, triage_result: Dict[str, Any]):
        """This now handles both new requests and follow-ups in threads."""
        try:
            user_id = str(message.author.id)
            thread_id = await self._get_or_create_thread(message, user_id)

            agent_message = {
                "type": "devrel_request",
                "id": f"discord_{message.id}",
                "user_id": user_id,
                "channel_id": str(message.channel.id),
                "thread_id": thread_id,
                "memory_thread_id": user_id,
                "content": message.content,
                "triage": triage_result,
                "classification": triage_result,
                "platform": "discord",
                "timestamp": message.created_at.isoformat(),
                "author": {
                    "username": message.author.name,
                    "display_name": message.author.display_name,
                    "avatar_url": str(message.author.avatar.url) if message.author.avatar else None
                }
            }
            priority_map = {"high": QueuePriority.HIGH,
                            "medium": QueuePriority.MEDIUM,
                            "low": QueuePriority.LOW
                            }
            priority = priority_map.get(triage_result.get("priority"), QueuePriority.MEDIUM)
            await self.queue_manager.enqueue(agent_message, priority)

            # --- "PROCESSING" MESSAGE RESTORED ---
            if thread_id:
                thread = self.get_channel(int(thread_id))
                if thread:
                    await thread.send("I'm processing your request, please hold on...")
            # ------------------------------------

        except Exception as e:
            logger.error(f"Error handling DevRel message: {str(e)}")

    async def _get_or_create_thread(self, message, user_id: str) -> Optional[str]:
        try:
            if user_id in self.active_threads:
                thread_id = self.active_threads[user_id]
                thread = self.get_channel(int(thread_id))
                if thread and not thread.archived:
                    return thread_id
                else:
                    del self.active_threads[user_id]

            # This part only runs if it's not a follow-up message in an active thread.
            if isinstance(message.channel, discord.TextChannel):
                thread_name = f"DevRel Chat - {message.author.display_name}"
                thread = await message.create_thread(name=thread_name, auto_archive_duration=60)
                self.active_threads[user_id] = str(thread.id)
                await thread.send(f"Hello {message.author.mention}! I've created this thread to help you. How can I assist?")
                return str(thread.id)
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
        return str(message.channel.id)

    async def _handle_agent_response(self, response_data: Dict[str, Any]):
        try:
            thread_id = response_data.get("thread_id")
            response_text = response_data.get("response", "")
            if not thread_id or not response_text:
                return
            thread = self.get_channel(int(thread_id))
            if thread:
                for i in range(0, len(response_text), 2000):
                    await thread.send(response_text[i:i+2000])
            else:
                logger.error(f"Thread {thread_id} not found for agent response")
        except Exception as e:
            logger.error(f"Error handling agent response: {str(e)}")
