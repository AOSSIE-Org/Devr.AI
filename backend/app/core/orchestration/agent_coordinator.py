import logging
import uuid
from typing import Dict, Any
from app.agents.devrel.agent import DevRelAgent
# TODO: Implement GitHub agent
# from app.agents.github.agent import GitHubAgent
from app.agents.shared.state import AgentState
from app.core.orchestration.queue_manager import AsyncQueueManager
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
        # TODO: Register GitHub agent handler after implementation
        # self.queue_manager.register_handler("github_request", self._handle_github_request)

    @traceable(name="devrel_request_coordination", run_type="tool")
    async def _handle_devrel_request(self, message_data: Dict[str, Any]):
        """Handle DevRel agent requests"""
        try:
            # Create agent state
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
            logger.info(f"Running DevRel agent for session {session_id}")
            result_state = await self.devrel_agent.run(initial_state)

            # Send response back to platform
            if result_state.final_response:
                await self._send_response_to_platform(message_data, result_state.final_response)

        except Exception as e:
            logger.error(f"Error handling DevRel request: {str(e)}")
            await self._send_error_response(message_data, "I'm having trouble processing your request. Please try again.")

    # TODO: Implement GitHub agent
    # async def _handle_github_request(self, message_data: Dict[str, Any]):
    #     """Handle GitHub agent requests"""
    #     try:
    #         # Implementation for GitHub agent
    #         session_id = str(uuid.uuid4())

    #         initial_state = AgentState(
    #             session_id=session_id,
    #             user_id=message_data.get("user_id", ""),
    #             platform="github",
    #             context={
    #                 "github_event": message_data.get("github_event", {}),
    #                 "event_type": message_data.get("event_type", "")
    #             }
    #         )

    #         # Run GitHub agent
    #         logger.info(f"Running GitHub agent for session {session_id}")
    #         result_state = await self.github_agent.run(initial_state)

    #         logger.info(f"GitHub agent completed for session {session_id}")

    #     except Exception as e:
    #         logger.error(f"Error handling GitHub request: {str(e)}")

    async def _send_response_to_platform(self, original_message: Dict[str, Any], response: str):
        """Send agent response back to the originating platform"""
        try:
            platform = original_message.get("platform", "discord")

            if platform == "discord":
                # Send response back to Discord queue for bot to handle
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

    @traceable(name="send_error_response", run_type="tool")
    async def _send_error_response(self, original_message: Dict[str, Any], error_message: str):
        """Send error response to platform"""
        await self._send_response_to_platform(original_message, error_message)
