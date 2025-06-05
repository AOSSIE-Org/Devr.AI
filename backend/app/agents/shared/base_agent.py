from typing import Dict, Any
import logging
from .state import AgentState

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base class for all LangGraph agents"""

    def __init__(self, agent_name: str, config: Dict[str, Any]):
        self.agent_name = agent_name
        self.config = config
        self.graph = None
        self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _build_graph")

    async def run(self, initial_state: AgentState) -> AgentState:
        """Execute the agent workflow"""
        try:
            logger.info("Starting %s for session %s", self.agent_name, initial_state.session_id)
            result = await self.graph.ainvoke(initial_state.model_dump())
            return AgentState(**result)
        except AttributeError as e:
            logger.error("Graph not properly initialized for %s: %s", self.agent_name, str(e))
            initial_state.errors.append(f"Agent initialization error: {str(e)}")
            return initial_state
        except Exception as e:
            logger.error("Error in %s: %s", self.agent_name, str(e))
            initial_state.errors.append(str(e))
            return initial_state

    async def stream_run(self, initial_state: AgentState):
        """Stream the agent execution for real-time updates"""
        async for step in self.graph.astream(initial_state.model_dump()):
            yield step
