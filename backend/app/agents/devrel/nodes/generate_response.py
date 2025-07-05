import logging
import json
from typing import Dict, Any
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
from ..prompts.response_prompt import RESPONSE_PROMPT

logger = logging.getLogger(__name__)

async def generate_response_node(state: AgentState, llm) -> Dict[str, Any]:
    """
    Final Response Generation Node
    """
    logger.info(f"Generating response for session {state.session_id}")

    try:
        final_response = await _create_response(state, llm)

        return {
            "final_response": final_response,
            "current_task": "response_generated"
        }

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return {
            "final_response": "I apologize, but I encountered an error while generating my response. Please try asking your question again.",
            "errors": state.errors + [str(e)],
            "current_task": "response_error"
        }

async def _create_response(state: AgentState, llm) -> str:
    """
    Response Generation and LLM synthesis
    """
    logger.info(f"Creating response for session {state.session_id}")

    latest_message = _get_latest_message(state)

    conversation_summary = state.conversation_summary or "This is the beginning of our conversation."

    recent_messages_count = min(10, len(state.messages))
    conversation_history = ""
    if state.messages:
        conversation_history = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in state.messages[-recent_messages_count:]
        ])

        if len(state.messages) > recent_messages_count:
            conversation_history = f"[Showing last {recent_messages_count} of {len(state.messages)} messages]\n" + \
                conversation_history
    else:
        conversation_history = "No previous conversation"

    context_parts = [
        f"Platform: {state.platform}",
        f"Total interactions: {state.interaction_count}",
        f"Session duration: {(state.last_interaction_time - state.session_start_time).total_seconds() / 60:.1f} minutes"
    ]

    if state.key_topics:
        context_parts.append(f"Key topics discussed: {', '.join(state.key_topics)}")
    if state.user_profile:
        context_parts.append(f"User profile: {state.user_profile}")

    current_context = "\n".join(context_parts)

    supervisor_thinking = state.context.get("supervisor_thinking", "No reasoning process available")

    tool_results = state.context.get("tool_results", [])
    tool_results_str = json.dumps(tool_results, indent=2) if tool_results else "No tool results"

    task_result = state.task_result or {}
    task_result_str = json.dumps(task_result, indent=2) if task_result else "No task result"

    try:
        prompt = RESPONSE_PROMPT.format(
            latest_message=latest_message,
            conversation_summary=conversation_summary,
            conversation_history=conversation_history,
            current_context=current_context,
            supervisor_thinking=supervisor_thinking,
            tool_results=tool_results_str,
            task_result=task_result_str
        )

        logger.info(f"Generated response prompt using existing RESPONSE_PROMPT")

    except KeyError as e:
        logger.error(f"Missing key in RESPONSE_PROMPT: {e}")
        return f"Error: Response template formatting error - {str(e)}"

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content.strip()

def _get_latest_message(state: AgentState) -> str:
    """Extract the latest message from state"""
    if state.messages:
        return state.messages[-1].get("content", "")
    return state.context.get("original_message", "")
