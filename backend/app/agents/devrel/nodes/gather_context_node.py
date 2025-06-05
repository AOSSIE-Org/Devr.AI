import logging
from app.agents.shared.state import AgentState

logger = logging.getLogger(__name__)

async def gather_context_node(state: AgentState) -> AgentState:
    """Gather additional context for the user and their request"""
    logger.info(f"Gathering context for session {state.session_id}")

    # TODO: Add context gathering from databases
    # Currently, context is simple
    # In production, query databases for user history, etc.
    context_data = {
        "user_profile": {"user_id": state.user_id, "platform": state.platform},
        "conversation_context": len(state.messages),
        "session_info": {"session_id": state.session_id}
    }

    state.context.update(context_data)
    state.current_task = "context_gathered"
    return state
