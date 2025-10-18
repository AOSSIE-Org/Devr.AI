import logging
from datetime import datetime
from typing import Dict, Any
from app.agents.state import AgentState
from app.database.supabase.services import ensure_user_exists, get_conversation_context

logger = logging.getLogger(__name__)

async def gather_context_node(state: AgentState) -> Dict[str, Any]:
    """Gather additional context for the user and their request"""
    logger.info(f"Gathering context for session {state.session_id}")

    original_message = state.context.get("original_message", "")
    author_info = state.context.get("author", {})

    # Ensure user exists in database
    user_uuid = await ensure_user_exists(
        user_id=state.user_id,
        platform=state.platform,
        username=author_info.get("username"),
        display_name=author_info.get("display_name"),
        avatar_url=author_info.get("avatar_url")
    )

    new_message = {
        "role": "user",
        "content": original_message,
        "timestamp": datetime.now().isoformat()
    }

    context_data = {
        "user_profile": {"user_id": state.user_id, "platform": state.platform},
        "conversation_context": len(state.messages) + 1,  # +1 for the new message
        "session_info": {"session_id": state.session_id},
        "user_uuid": user_uuid
    }

    # Only retrieve from database if we don't have conversation context already
    should_fetch_from_db = not state.conversation_summary and not state.key_topics

    if user_uuid and should_fetch_from_db:
        logger.info(f"No existing context in state, fetching from database for user {user_uuid}")
        prev_context = await get_conversation_context(user_uuid)
        if prev_context:
            logger.info(f"Retrieved previous conversation context from database")
            context_data["previous_conversation"] = prev_context

            # Populate state with previous conversation summary and topics
            return {
                "messages": [new_message],
                "context": {**state.context, **context_data},
                "conversation_summary": prev_context.get("conversation_summary"),
                "key_topics": prev_context.get("key_topics", []),
                "current_task": "context_gathered",
                "last_interaction_time": datetime.now()
            }
        else:
            logger.info(f"No previous conversation context found in database")
    else:
        if not should_fetch_from_db:
            logger.info(
                f"Using existing context from state (conversation_summary: {bool(state.conversation_summary)}, key_topics: {len(state.key_topics)})")

    updated_context = {**state.context, **context_data}

    return {
        "messages": [new_message],
        "context": updated_context,
        "current_task": "context_gathered",
        "last_interaction_time": datetime.now()
    }
