import logging
import json
from typing import Dict, Any, Literal
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
from ..prompts.react_prompt import REACT_SUPERVISOR_PROMPT

logger = logging.getLogger(__name__)

async def react_supervisor_node(state: AgentState, llm) -> Dict[str, Any]:
    """ReAct Supervisor: Think -> Act -> Observe"""
    logger.info(f"ReAct Supervisor thinking for session {state.session_id}")

    # Get current context
    latest_message = _get_latest_message(state)
    conversation_history = _get_conversation_history(state)
    tool_results = state.context.get("tool_results", [])
    iteration_count = state.context.get("iteration_count", 0)

    forced_action = state.context.get("force_next_tool")
    if forced_action:
        logger.info(
            "Supervisor auto-routing to %s for session %s", forced_action, state.session_id
        )
        decision = {
            "action": forced_action,
            "reasoning": "Auto-routed by onboarding workflow",
            "thinking": "",
        }
        updated_context = {**state.context}
        updated_context.pop("force_next_tool", None)
        updated_context["supervisor_decision"] = decision
        updated_context["iteration_count"] = iteration_count + 1
        return {
            "context": updated_context,
            "current_task": f"supervisor_forced_{forced_action}",
        }

    if state.context.get("force_complete"):
        logger.info("Supervisor forcing completion for session %s", state.session_id)
        decision = {
            "action": "complete",
            "reasoning": "Auto-complete after onboarding hand-off",
            "thinking": "",
        }
        updated_context = {**state.context}
        updated_context.pop("force_complete", None)
        updated_context["supervisor_decision"] = decision
        updated_context["iteration_count"] = iteration_count + 1
        return {
            "context": updated_context,
            "current_task": "supervisor_forced_complete",
        }

    prompt = REACT_SUPERVISOR_PROMPT.format(
        latest_message=latest_message,
        platform=state.platform,
        interaction_count=state.interaction_count,
        iteration_count=iteration_count,
        conversation_history=conversation_history,
        tool_results=json.dumps(tool_results, indent=2) if tool_results else "No previous tool results"
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    decision = _parse_supervisor_decision(response.content)

    logger.info(f"ReAct Supervisor decision: {decision['action']}")

    # Update state with supervisor's thinking
    return {
        "context": {
            **state.context,
            "supervisor_thinking": response.content,
            "supervisor_decision": decision,
            "iteration_count": iteration_count + 1
        },
        "current_task": f"supervisor_decided_{decision['action']}"
    }

def _parse_supervisor_decision(response: str) -> Dict[str, Any]:
    """Parse the supervisor's decision from LLM response"""
    try:
        lines = response.strip().split('\n')
        decision = {"action": "complete", "reasoning": "", "thinking": ""}

        for line in lines:
            if line.startswith("THINK:"):
                decision["thinking"] = line.replace("THINK:", "").strip()
            elif line.startswith("ACT:"):
                action = line.replace("ACT:", "").strip().lower()
                if action in ["web_search", "faq_handler", "onboarding", "github_toolkit", "complete"]:
                    decision["action"] = action
            elif line.startswith("REASON:"):
                decision["reasoning"] = line.replace("REASON:", "").strip()

        return decision
    except Exception as e:
        logger.error(f"Error parsing supervisor decision: {e}")
        return {"action": "complete", "reasoning": "Error in decision parsing", "thinking": ""}

def supervisor_decision_router(state: AgentState) -> Literal["web_search", "faq_handler", "onboarding", "github_toolkit", "complete"]:
    """Route based on supervisor's decision"""
    decision = state.context.get("supervisor_decision", {})
    action = decision.get("action", "complete")

    # Safety check for infinite loops
    iteration_count = state.context.get("iteration_count", 0)
    if iteration_count > 10:
        logger.warning(f"Max iterations reached for session {state.session_id}")
        return "complete"

    return action

def add_tool_result(state: AgentState, tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Add tool result to state context"""
    tool_results = state.context.get("tool_results", [])
    tool_results.append({
        "tool": tool_name,
        "result": result,
        "iteration": state.context.get("iteration_count", 0)
    })

    return {
        "context": {
            **state.context,
            "tool_results": tool_results
        },
        "tools_used": state.tools_used + [tool_name],
        "current_task": f"completed_{tool_name}"
    }

def _get_latest_message(state: AgentState) -> str:
    """Extract the latest message from state"""
    if state.messages:
        return state.messages[-1].get("content", "")
    return state.context.get("original_message", "")

def _get_conversation_history(state: AgentState, max_messages: int = 5) -> str:
    """Get formatted conversation history"""
    if not state.messages:
        return "No previous conversation"

    recent_messages = state.messages[-max_messages:]
    return "\n".join([
        f"{msg.get('role', 'user')}: {msg.get('content', '')}"
        for msg in recent_messages
    ])
