import logging
from datetime import datetime
from typing import Any, Dict

from app.agents.state import AgentState
from app.services.auth.management import get_or_create_user_by_discord

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

    profile_data: Dict[str, Any] = dict(state.user_profile or {})

    if state.platform.lower() == "discord":
        author = state.context.get("author", {}) or {}
        discord_id = author.get("id") or state.user_id
        display_name = author.get("display_name") or author.get("global_name") or author.get("name") or author.get("username")
        discord_username = author.get("username") or author.get("name") or author.get("display_name")
        avatar_url = author.get("avatar") or author.get("avatar_url")

        if discord_id:
            try:
                user = await get_or_create_user_by_discord(
                    discord_id=str(discord_id),
                    display_name=str(display_name or discord_username or discord_id),
                    discord_username=str(discord_username or display_name or discord_id),
                    avatar_url=avatar_url,
                )
                profile_data = user.model_dump()
            except Exception as exc:  # pragma: no cover - graceful degradation
                logger.warning("Failed to refresh Discord user profile for %s: %s", discord_id, exc)

    context_data = {
        "user_profile": profile_data or {"user_id": state.user_id, "platform": state.platform},
        "conversation_context": len(state.messages) + 1,  # +1 for the new message
        "session_info": {"session_id": state.session_id}
    }

    updated_context = {**state.context, **context_data}

    result: Dict[str, Any] = {
        "messages": [new_message],
        "context": updated_context,
        "current_task": "context_gathered",
        "last_interaction_time": datetime.now(),
    }

    if profile_data:
        result["user_profile"] = profile_data

    return result
