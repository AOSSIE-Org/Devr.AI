import logging
import uuid
from typing import Dict, Any
from datetime import datetime
from app.agents.devrel.agent import DevRelAgent
# TODO: Implement GitHub agent
# from app.agents.github.agent import GitHubAgent
from app.agents.state import AgentState
from app.core.orchestration.queue_manager import AsyncQueueManager
from app.agents.devrel.nodes.summarization import store_summary_to_database
from langsmith import traceable

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """Coordinates agent execution and response handling"""

    def __init__(self, queue_manager: AsyncQueueManager):
        self.queue_manager = queue_manager
        self.devrel_agent = DevRelAgent()
        # self.github_agent = GitHubAgent()
        self.active_sessions: Dict[str, AgentState] = {}

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register message handlers"""
        self.queue_manager.register_handler("devrel_request", self._handle_devrel_request)
        self.queue_manager.register_handler("clear_thread_memory", self._handle_clear_memory_request)
        # TODO: Register GitHub agent handler after implementation
        # self.queue_manager.register_handler("github_request", self._handle_github_request)

    @traceable(name="devrel_request_coordination", run_type="chain")
    async def _handle_devrel_request(self, message_data: Dict[str, Any]):
        """Handle DevRel agent requests"""
        try:
            # Extract memory thread ID (user_id for Discord)
            memory_thread_id = message_data.get("memory_thread_id") or message_data.get("user_id", "")
            session_id = str(uuid.uuid4())

            initial_state = AgentState(
                session_id=session_id,
                user_id=message_data.get("user_id", ""),
                platform=message_data.get("platform", "discord"),
                thread_id=message_data.get("thread_id"),
                channel_id=message_data.get("channel_id"),
                context={
                    "original_message": message_data.get("content", ""),
                    "classification": message_data.get("classification", {}),
                    "author": message_data.get("author", {})
                }
            )

            # Run agent
            logger.info(f"Running DevRel agent for session {session_id} with memory thread {memory_thread_id}")
            result_state = await self.devrel_agent.run(initial_state, memory_thread_id)

            # Check if thread timeout was reached during processing
            if result_state.memory_timeout_reached:
                await self._handle_memory_timeout(memory_thread_id, result_state)

            # Send response back to platform
            if result_state.final_response:
                await self._send_response_to_platform(message_data, result_state.final_response)

        except Exception as e:
            logger.error(f"Error handling DevRel request: {str(e)}")
            await self._send_error_response(message_data, "I'm having trouble processing your request. Please try again.")

    async def _handle_clear_memory_request(self, message_data: Dict[str, Any]):
        """Handle requests to clear thread memory"""
        try:
            memory_thread_id = message_data.get("memory_thread_id")
            cleanup_reason = message_data.get("cleanup_reason", "manual")

            if not memory_thread_id:
                logger.warning("No memory_thread_id provided for memory clear request")
                return

            logger.info(f"Clearing memory for thread {memory_thread_id}, reason: {cleanup_reason}")

            # Clear from InMemorySaver
            success = await self.devrel_agent.clear_thread_memory(memory_thread_id, force_clear=True)

            if success:
                logger.info(f"Successfully cleared memory for thread {memory_thread_id}")
            else:
                logger.error(f"Failed to clear memory for thread {memory_thread_id}")

        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")

    async def _handle_memory_timeout(self, memory_thread_id: str, state: AgentState):
        """Handle memory timeout - store to database and clear from InMemorySaver"""
        try:
            logger.info(f"Handling memory timeout for thread {memory_thread_id}")

            # Store final summary to database
            await store_summary_to_database(state)

            # Clear from InMemorySaver
            await self.devrel_agent.clear_thread_memory(memory_thread_id, force_clear=True)

            logger.info(f"Memory timeout handled successfully for thread {memory_thread_id}")

        except Exception as e:
            logger.error(f"Error handling memory timeout: {str(e)}")

    async def _send_response_to_platform(self, original_message: Dict[str, Any], response: str):
        """Send agent response back to the originating platform"""
        try:
            platform = original_message.get("platform", "discord")

            if platform == "discord":
                response_message = {
                    "type": "discord_response",
                    "thread_id": original_message.get("thread_id"),
                    "channel_id": original_message.get("channel_id"),
                    "response": response,
                    "original_message_id": original_message.get("id")
                }

                await self.queue_manager.enqueue(response_message)

        except Exception as e:
            logger.error(f"Error sending response to platform: {str(e)}")

    async def _send_error_response(self, original_message: Dict[str, Any], error_message: str):
        """Send error response to platform"""
        await self._send_response_to_platform(original_message, error_message)

    # TODO: Implement GitHub agent
    # async def _handle_github_request(self, message_data: Dict[str, Any]):
