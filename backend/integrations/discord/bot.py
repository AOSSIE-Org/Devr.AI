import discord
from discord.ext import commands
from discord.ui import View
import logging
from typing import Dict, Any, Optional
from app.core.orchestration.queue_manager import AsyncQueueManager, QueuePriority
from app.classification.classification_router import ClassificationRouter
from datetime import datetime

class HumanReviewView(View):
    def __init__(self, bot, session_id: str):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.bot = bot
        self.session_id = session_id
        self.user_response = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_response = "confirm"
        await interaction.response.send_message("You confirmed the action.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_response = "cancel"
        await interaction.response.send_message("You cancelled the action.", ephemeral=True)
        self.stop()


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
                "platform": "discord",
                "timestamp": message.created_at.isoformat(),
                "author": {
                    "username": message.author.name,
                    "display_name": message.author.display_name
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
            context = response_data.get("context", {})

            if not thread_id:
                return

            thread = self.get_channel(int(thread_id))
            if not thread:
                logger.error(f"Thread {thread_id} not found for agent response")
                return

            # Check if waiting for user input (Human-in-the-Loop)
            if context.get("waiting_for_user_input", False):
                view = HumanReviewView(self, response_data.get("session_id"))
                await thread.send(content=context["interrupt_details"]["prompt"], view=view)

                # Wait for user interaction or timeout
                await view.wait()

                if view.user_response is not None:
                    # Process user feedback with helper method
                    await self.process_human_feedback(response_data.get("session_id"), view.user_response)
                else:
                    await thread.send("Timed out waiting for response. Continuing without human input.")
            else:
                # Send normal response message chunks
                for i in range(0, len(response_text), 2000):
                    await thread.send(response_text[i:i+2000])

        except Exception as e:
            logger.error(f"Error handling agent response: {str(e)}")

    async def process_human_feedback(self, session_id: str, feedback: str):
        logger.info(f"Received human feedback for session {session_id}: {feedback}")

        agent_state = await self.agent_coordinator.load_agent_state(session_id)
        if not agent_state:
            logger.error(f"AgentState not found for session {session_id}")
            return

        agent_state.human_feedback = feedback
        agent_state.requires_human_review = False
        agent_state.context["waiting_for_user_input"] = False
        agent_state.context["interrupt_details"] = {}

        await self.agent_coordinator.save_agent_state(agent_state)

        continuation_message = {
            "type": "devrel_request",
            "session_id": agent_state.session_id,
            "user_id": agent_state.user_id,
            "channel_id": agent_state.channel_id,
            "thread_id": agent_state.thread_id,
            "memory_thread_id": agent_state.user_id,
            "content": f"User feedback: {feedback}",
            "platform": agent_state.platform,
            "timestamp": datetime.utcnow().isoformat(),
            "author": {
                "username": "human_reviewer",
                "display_name": "Human Reviewer",
            }
        }

        await self.queue_manager.enqueue(continuation_message, QueuePriority.HIGH)
