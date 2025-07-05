import logging
from datetime import datetime
from typing import Dict, Any
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

async def gather_context_node(state: AgentState) -> Dict[str, Any]:
    """Gather additional context for the user and their request"""
    logger.info(f"Gathering context for session {state.session_id}")

    # TODO: Add context gathering from databases
    # Currently, context is simple
    # In production, query databases for user history, etc.

    original_message = state.context.get("original_message", "")

    new_message = {
        "role": "user",
        "content": original_message,
        "timestamp": datetime.now().isoformat()
    }

    context_data = {
        "user_profile": {"user_id": state.user_id, "platform": state.platform},
        "conversation_context": len(state.messages) + 1,  # +1 for the new message
        "session_info": {"session_id": state.session_id}
    }

    updated_context = {**state.context, **context_data}

    return {
        "messages": [new_message],
        "context": updated_context,
        "current_task": "context_gathered",
        "last_interaction_time": datetime.now()
    }
