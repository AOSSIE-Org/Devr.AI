import logging
from app.agents.shared.state import AgentState

logger = logging.getLogger(__name__)

async def handle_onboarding_node(state: AgentState) -> AgentState:
    """Handle onboarding requests"""
    logger.info(f"Handling onboarding for session {state.session_id}")

    state.task_result = {
        "type": "onboarding",
        "action": "welcome_and_guide",
        "next_steps": ["setup_environment", "first_contribution", "join_community"]
    }

    state.current_task = "onboarding_handled"
    return state
