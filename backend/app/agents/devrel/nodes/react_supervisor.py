import json
import logging
from datetime import datetime
from typing import Dict, Any, Literal
from langchain_core.messages import HumanMessage

from app.agents.state import AgentState
from ..prompts.react_prompt import REACT_SUPERVISOR_PROMPT
from ..nodes.generate_response import _get_latest_message as get_latest_message_util

logger = logging.getLogger(__name__)

# Configuration constants
MAX_ITERATIONS = 10
MAX_CONVERSATION_HISTORY = 5
VALID_ACTIONS = ["web_search", "faq_handler", "onboarding", "github_toolkit", "complete"]


async def react_supervisor_node(state: AgentState, llm) -> Dict[str, Any]:
    """ReAct Supervisor: Think -> Act -> Observe"""

    if not _validate_state(state):
        logger.error(f"Invalid state for session {getattr(state, 'session_id', 'unknown')}")
        return _create_error_response(state, "Invalid state")

    logger.info(f"ReAct Supervisor thinking for session {state.session_id}")

    latest_message = _get_latest_message(state)
    conversation_history = _get_conversation_history(state)
    tool_results = state.context.get("tool_results", [])
    iteration_count = state.context.get("iteration_count", 0)

    # Safety check for max iterations
    if iteration_count >= MAX_ITERATIONS:
        logger.warning(f"Max iterations ({MAX_ITERATIONS}) reached for session {state.session_id}")
        return _create_completion_response(state, "Maximum iterations reached")

    # Safely serialize tool_results for prompt usage
    try:
        if tool_results:
            tool_results_str = json.dumps(tool_results, indent=2, default=str)
        else:
            tool_results_str = "No previous tool results"
    except Exception as e:
        logger.warning(f"Failed to serialize tool_results: {e}")
        tool_results_str = str(tool_results) if tool_results else "No previous tool results"

    prompt = REACT_SUPERVISOR_PROMPT.format(
        latest_message=latest_message,
        platform=getattr(state, 'platform', 'unknown'),
        interaction_count=getattr(state, 'interaction_count', 0),
        iteration_count=iteration_count,
        conversation_history=conversation_history,
        tool_results=tool_results_str
    )

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        decision = _parse_supervisor_decision(response.content)

        logger.debug(f"Current iteration: {iteration_count}")
        logger.debug(f"Latest message length: {len(latest_message or '')}")
        logger.info(f"ReAct Supervisor decision: {decision['action']}")
        logger.debug(f"Supervisor thinking: {decision.get('thinking', '')[:100]}...")
        logger.debug(f"Supervisor reasoning: {decision.get('reasoning', '')[:100]}...")

        return {
            "context": {
                **state.context,
                "supervisor_thinking": response.content,
                "supervisor_decision": decision,
                "iteration_count": iteration_count + 1,
                "last_action": decision['action']
            },
            "current_task": f"supervisor_decided_{decision['action']}"
        }

    except Exception as e:
        logger.error(f"Error in react_supervisor_node: {e}", exc_info=True)
        return _create_error_response(state, f"Supervisor error: {str(e)}")


def _parse_supervisor_decision(response: str) -> Dict[str, Any]:
    """Parse the supervisor's decision from LLM response with better handling."""
    decision = {"action": "complete", "reasoning": "", "thinking": ""}

    try:
        if not response or not response.strip():
            logger.warning("Empty response from supervisor, defaulting to complete")
            return decision

        current_section = None
        content_buffer = []

        for line in response.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.startswith("THINK:"):
                if current_section and content_buffer:
                    decision[current_section] = " ".join(content_buffer)
                current_section = "thinking"
                content_buffer = [line.replace("THINK:", "").strip()]

            elif line.startswith("ACT:"):
                if current_section and content_buffer:
                    decision[current_section] = " ".join(content_buffer)
                action = line.replace("ACT:", "").strip().lower()
                if action in VALID_ACTIONS:
                    decision["action"] = action
                else:
                    logger.warning(f"Invalid action '{action}', defaulting to 'complete'")
                    decision["action"] = "complete"
                current_section = None
                content_buffer = []

            elif line.startswith("REASON:"):
                if current_section and content_buffer:
                    decision[current_section] = " ".join(content_buffer)
                current_section = "reasoning"
                content_buffer = [line.replace("REASON:", "").strip()]

            elif current_section and line:
                content_buffer.append(line)

        if current_section and content_buffer:
            decision[current_section] = " ".join(content_buffer)

        if decision["action"] not in VALID_ACTIONS:
            logger.warning(f"Final validation failed for action '{decision['action']}', defaulting to 'complete'")
            decision["action"] = "complete"

    except Exception as e:
        logger.error(f"Error parsing supervisor decision: {e}", exc_info=True)

    return decision


def supervisor_decision_router(state: AgentState) -> Literal["web_search", "faq_handler", "onboarding", "github_toolkit", "complete"]:
    """Route based on supervisor's decision"""
    try:
        decision = state.context.get("supervisor_decision", {})
        action = decision.get("action", "complete")

        iteration_count = state.context.get("iteration_count", 0)
        if iteration_count > MAX_ITERATIONS:
            logger.warning(f"Max iterations reached for session {state.session_id}")
            return "complete"

        if action not in VALID_ACTIONS:
            logger.warning(f"Invalid routing action '{action}', defaulting to 'complete'")
            return "complete"

        logger.debug(f"Routing to: {action} (iteration {iteration_count})")
        return action

    except Exception as e:
        logger.error(f"Error in supervisor_decision_router: {e}", exc_info=True)
        return "complete"


def add_tool_result(state: AgentState, tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Add tool result to state context with validation"""
    try:
        if not _validate_state(state):
            logger.error("Invalid state in add_tool_result")
            return {"context": state.context if hasattr(state, 'context') else {}}

        tool_results = state.context.get("tool_results", [])

        if not isinstance(result, dict):
            logger.warning(f"Tool result for {tool_name} is not a dict, converting")
            result = {"result": str(result)}

        tool_entry = {
            "tool": tool_name,
            "result": result,
            "iteration": state.context.get("iteration_count", 0),
            "timestamp": datetime.now().isoformat()
        }

        tool_results.append(tool_entry)

        if len(tool_results) > 20:
            tool_results = tool_results[-20:]
            logger.debug("Trimmed tool results to last 20 entries")

        tools_used = getattr(state, 'tools_used', []) + [tool_name]

        return {
            "context": {
                **state.context,
                "tool_results": tool_results
            },
            "tools_used": tools_used,
            "current_task": f"completed_{tool_name}"
        }

    except Exception as e:
        logger.error(f"Error in add_tool_result: {e}", exc_info=True)
        return {"context": state.context if hasattr(state, 'context') else {}}


def _get_latest_message(state: AgentState) -> str:
    """Extract the latest message from state"""
    try:
        return get_latest_message_util(state)
    except Exception as e:
        logger.error(f"Error getting latest message: {e}", exc_info=True)
        return ""


def _get_conversation_history(state: AgentState, max_messages: int = MAX_CONVERSATION_HISTORY) -> str:
    """Get formatted conversation history"""
    try:
        if not getattr(state, 'messages', None):
            return "No previous conversation"

        recent_messages = state.messages[-max_messages:]
        formatted_messages = []
        for msg in recent_messages:
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if content:
                    formatted_messages.append(
                        f"{role}: {content[:200]}{'...' if len(content) > 200 else ''}"
                    )
        return "\n".join(formatted_messages) if formatted_messages else "No previous conversation"

    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        return "Error retrieving conversation history"


def _validate_state(state: AgentState) -> bool:
    """Validate state before processing"""
    try:
        if not state:
            return False
        if not getattr(state, 'session_id', None):
            logger.error("Invalid state: missing session_id")
            return False
        if not hasattr(state, 'context'):
            logger.error("Invalid state: missing context")
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating state: {e}", exc_info=True)
        return False


def _create_error_response(state: AgentState, error_message: str) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "context": {
            **(state.context if hasattr(state, 'context') else {}),
            "supervisor_decision": {
                "action": "complete",
                "reasoning": error_message,
                "thinking": "Error occurred"
            },
            "error": error_message
        },
        "current_task": "supervisor_decided_complete"
    }


def _create_completion_response(state: AgentState, reason: str) -> Dict[str, Any]:
    """Create standardized completion response"""
    return {
        "context": {
            **state.context,
            "supervisor_decision": {
                "action": "complete",
                "reasoning": reason,
                "thinking": "Completing task"
            },
            "completion_reason": reason
        },
        "current_task": "supervisor_decided_complete"
    }
