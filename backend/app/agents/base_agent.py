from typing import Dict, Any, AsyncGenerator
from abc import ABC, abstractmethod
import logging
from .state import AgentState

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all LangGraph agents"""

    def __init__(self, agent_name: str, config: Dict[str, Any]):
        self.agent_name = agent_name
        self.config = config
        self.graph = None
        self._build_graph()

    @abstractmethod
    def _build_graph(self):
        """Build the LangGraph workflow - to be implemented by subclasses"""
        pass

    async def run(self, initial_state: AgentState, thread_id: str) -> AgentState:
        """Execute the agent workflow with memory persistence"""
        try:
            logger.info(f"Starting {self.agent_name} for session {initial_state.session_id}")
            config = {"configurable": {"thread_id": thread_id}}
            existing_state = self.graph.get_state(config)

            if existing_state and existing_state.values:
                existing_agent_state = AgentState(**existing_state.values)
                logger.info(f"RECOVERED existing state for thread {thread_id}:")
                logger.info(f"  - Messages: {len(existing_agent_state.messages)}")
                logger.info(f"  - Summary: '{existing_agent_state.conversation_summary or 'None'}'")
                logger.info(f"  - Summary length: {len(existing_agent_state.conversation_summary or '')} chars")
                logger.info(f"  - Topics: {existing_agent_state.key_topics}")
                logger.info(f"  - Interaction count: {existing_agent_state.interaction_count}")
                logger.info(f"  - Session start: {existing_agent_state.session_start_time}")
            else:
                logger.info(f"No existing state found for thread {thread_id} - starting fresh")

            logger.info(f"Running {self.agent_name} with memory for thread {thread_id}")

            result = await self.graph.ainvoke(initial_state.model_dump(), config)
            return AgentState(**result)
        except AttributeError as e:
            logger.error("Graph not properly initialized for %s: %s", self.agent_name, str(e), exc_info=True)
            state_dict = initial_state.model_dump()
            state_dict['errors'].append(f"Agent initialization error: {str(e)}")
            return AgentState(**state_dict)
        except Exception as e:
            logger.error("Error in %s: %s", self.agent_name, str(e), exc_info=True)
            state_dict = initial_state.model_dump()
            state_dict['errors'].append(str(e))
            return AgentState(**state_dict)

    async def stream_run(self, initial_state: AgentState, thread_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the agent execution for real-time updates"""
        try:
            if not self.graph:
                raise AttributeError("Graph not properly initialized")
            config = {"configurable": {"thread_id": thread_id}}
            logger.info(f"Streaming with memory for thread {thread_id}")
            existing_state = self.graph.get_state(config)
            if existing_state and existing_state.values:
                existing_agent_state = AgentState(**existing_state.values)
                logger.info(f"Streaming with existing state: {len(existing_agent_state.messages)} messages, "
                            f"interaction count: {existing_agent_state.interaction_count}")

            step_count = 0
            async for step in self.graph.astream(initial_state.model_dump(), config):
                step_count += 1
                logger.debug(f"Stream step {step_count}: {list(step.keys())}")
                yield step

            logger.info(f"Streaming completed after {step_count} steps")
        except Exception as e:
            logger.error("Error in %s stream: %s", self.agent_name, str(e), exc_info=True)
            yield {"error": str(e)}
