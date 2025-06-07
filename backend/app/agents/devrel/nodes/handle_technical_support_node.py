import logging
from app.agents.shared.state import AgentState
from langsmith import traceable

logger = logging.getLogger(__name__)

@traceable(name="handle_technical_support_node", run_type="tool")
async def handle_technical_support_node(state: AgentState) -> AgentState:
    """Handle technical support requests"""
    logger.info(f"Handling technical support for session {state.session_id}")

    state.task_result = {
        "type": "technical_support",
        "action": "provide_guidance",
        "requires_human_review": False
    }

    state.current_task = "technical_support_handled"
    return state
