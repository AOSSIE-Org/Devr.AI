import logging
from typing import Any, Dict

from app.agents.devrel.onboarding.workflow import (
    OnboardingStage,
    run_onboarding_flow,
)
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

def _latest_text(state: AgentState) -> str:
    if state.messages:
        return state.messages[-1].get("content", "").lower()
    return state.context.get("original_message", "").lower()

async def handle_onboarding_node(state: AgentState) -> Dict[str, Any]:
    """Handle onboarding requests via the multi-stage onboarding workflow."""
    logger.info(f"Handling onboarding for session {state.session_id}")

    text = _latest_text(state)

    # Try to derive verification state if present in context/user_profile
    is_verified = False
    github_username = None
    try:
        profile = state.user_profile or {}
        ctx_profile = state.context.get("user_profile", {})
        is_verified = bool(profile.get("is_verified") or ctx_profile.get("is_verified"))
        github_username = profile.get("github_username") or ctx_profile.get("github_username")
    except Exception:
        pass

    flow_result, updated_state = run_onboarding_flow(
        state=state,
        latest_message=text,
        is_verified=is_verified,
        github_username=github_username,
    )

    task_result: Dict[str, Any] = {
        "type": "onboarding",
        "stage": flow_result.stage.value,
        "status": flow_result.status,
        "welcome_message": flow_result.welcome_message,
        "final_message": flow_result.final_message,
        "actions": flow_result.actions,
        "is_verified": flow_result.is_verified,
        "capability_sections": flow_result.capability_sections,
    }

    if flow_result.route_hint:
        task_result["route_hint"] = flow_result.route_hint
    if flow_result.handoff:
        task_result["handoff"] = flow_result.handoff
    if flow_result.next_tool:
        task_result["next_tool"] = flow_result.next_tool
    if flow_result.metadata:
        task_result["metadata"] = flow_result.metadata

    current_task = f"onboarding_{flow_result.stage.value}"

    return {
        "task_result": task_result,
        "current_task": current_task,
        "onboarding_state": updated_state,
    }
