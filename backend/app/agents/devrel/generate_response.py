import logging
from typing import Dict, Any
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
from .prompts.response_prompt import RESPONSE_PROMPT
from .nodes.handlers.web_search import create_search_response

logger = logging.getLogger(__name__)


async def _create_llm_response(state: AgentState, task_result: Dict[str, Any], llm) -> str:
    """Generate a response using the LLM based on the current state and task result."""
    logger.info(f"Creating LLM response for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    conversation_summary = state.conversation_summary or "This is the beginning of our conversation."

    recent_messages_count = min(10, len(state.messages))
    conversation_history_str = "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}"
        for msg in state.messages[-recent_messages_count:]
    ])

    total_messages = len(state.messages)
    if total_messages > recent_messages_count:
        conversation_history_str = f"[Showing last {recent_messages_count} of {total_messages} messages]\n" + \
            conversation_history_str

    context_parts = [
        f"Platform: {state.platform}",
        f"Total interactions: {state.interaction_count}",
        f"Session duration: {(state.last_interaction_time - state.session_start_time).total_seconds() / 60:.1f} minutes"
    ]

    if state.key_topics:
        context_parts.append(f"Key topics discussed: {', '.join(state.key_topics)}")

    if state.user_profile:
        context_parts.append(f"User profile: {state.user_profile}")

    current_context_str = "\n".join(context_parts)

    try:
        prompt = RESPONSE_PROMPT.format(
            conversation_summary=conversation_summary,
            latest_message=latest_message,
            conversation_history=conversation_history_str,
            current_context=current_context_str,
            task_type=task_result.get("type", "general"),
            task_details=str(task_result)
        )

        logger.info(f"Prompt includes summary: {len(conversation_summary)} chars, "
                    f"recent history: {recent_messages_count} messages, "
                    f"total history: {total_messages} messages")
    except KeyError as e:
        logger.error(f"Missing key in GENERAL_LLM_RESPONSE_PROMPT: {e}")
        return "Error: Response template formatting error."

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content.strip()

async def generate_response_node(state: AgentState, llm) -> dict:
    """Generate final response to user"""
    logger.info(f"Generating response for session {state.session_id}")
    task_result = state.task_result or {}

    if task_result.get("type") == "faq":
        final_response = task_result.get("response", "I don't have a specific answer for that question.")
    elif task_result.get("type") == "web_search":
        final_response = create_search_response(task_result)
    else:
        final_response = await _create_llm_response(state, task_result, llm)

    return {
        "final_response": final_response,
        "current_task": "response_generated"
    }
