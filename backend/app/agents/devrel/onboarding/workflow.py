"""Onboarding workflow state machine used by the onboarding tool node."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from app.agents.devrel.onboarding import messages
from app.agents.state import AgentState

class OnboardingStage(str, Enum):
    """Discrete stages in the onboarding flow."""

    INTRO = "intro"
    AWAITING_CHOICE = "awaiting_choice"
    ENCOURAGE_VERIFICATION = "encourage_verification"
    VERIFIED_CAPABILITIES = "verified_capabilities"
    COMPLETED = "completed"


@dataclass
class OnboardingFlowResult:
    """Structured response produced by the onboarding workflow."""

    stage: OnboardingStage
    status: str
    welcome_message: str
    actions: List[Dict[str, str]] = field(default_factory=list)
    final_message: Optional[str] = None
    is_verified: bool = False
    capability_sections: Optional[List[Dict[str, Any]]] = None
    route_hint: Optional[str] = None
    handoff: Optional[str] = None
    next_tool: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


_INTENT_VERIFIED = re.compile(r"\b(i\s*(have)?\s*)?(linked|connected|verified)\b.*github", re.IGNORECASE)
_INTENT_SKIP = re.compile(r"\b(skip|later|not\s+now)\b", re.IGNORECASE)
_INTENT_HELP = re.compile(r"\b(how|help|can't|cannot|stuck)\b.*verify", re.IGNORECASE)
_INTENT_EXPLORE = re.compile(
    r"\b(repo|repository|issue|issues|project|projects|org|organisation|organization|contribute|task)\b",
    re.IGNORECASE,
)


def _detect_user_intent(message: str) -> str:
    if not message:
        return "none"

    text = message.strip().lower()

    if _INTENT_VERIFIED.search(text):
        return "confirm_verified"
    if _INTENT_SKIP.search(text):
        return "skip"
    if _INTENT_HELP.search(text):
        return "help_verify"
    if _INTENT_EXPLORE.search(text):
        return "explore"

    return "none"


def _base_actions(include_verification: bool = True) -> List[Dict[str, str]]:
    actions: List[Dict[str, str]] = []
    if include_verification:
        actions.extend(
            [
                {"type": "suggest_command", "command": "/verify_github"},
                {"type": "suggest_command", "command": "/verification_status"},
            ]
        )
    actions.append({"type": "suggest_command", "command": "/help"})
    return actions


def _exploration_suggestions() -> List[Dict[str, str]]:
    return [
        {"type": "suggest_message", "content": "Show me our most active repositories."},
        {"type": "suggest_message", "content": "Are there any 'good first issues' available?"},
        {"type": "suggest_message", "content": "Give me an overview of the 'Devr.AI-backend' repo."},
    ]


def run_onboarding_flow(
    state: AgentState,
    latest_message: str,
    is_verified: bool,
    github_username: Optional[str],
) -> Tuple[OnboardingFlowResult, Dict[str, Any]]:
    """Execute the onboarding state machine and return response + updated state."""

    onboarding_state = dict(state.onboarding_state or {})
    stage = onboarding_state.get("stage", OnboardingStage.INTRO.value)
    try:
        stage_enum = OnboardingStage(stage)
    except ValueError:
        stage_enum = OnboardingStage.INTRO

    intent = _detect_user_intent(latest_message)

    reminders_sent = int(onboarding_state.get("reminders_sent", 0))
    capability_sections = messages.CAPABILITY_SECTIONS

    if stage_enum is OnboardingStage.INTRO:
        if is_verified:
            onboarding_state["stage"] = OnboardingStage.VERIFIED_CAPABILITIES.value
            onboarding_state["verified_acknowledged"] = True
            intro = messages.build_verified_capabilities_intro(github_username)
            return (
                OnboardingFlowResult(
                    stage=OnboardingStage.VERIFIED_CAPABILITIES,
                    status="completed",
                    welcome_message=intro,
                    final_message=messages.render_capabilities_text(),
                    actions=_exploration_suggestions(),
                    is_verified=True,
                    capability_sections=capability_sections,
                    route_hint="onboarding",
                    handoff="github_toolkit",
                    next_tool="github_toolkit",
                ),
                onboarding_state,
            )

        onboarding_state["stage"] = OnboardingStage.AWAITING_CHOICE.value
        onboarding_state.setdefault("reminders_sent", reminders_sent)
        return (
            OnboardingFlowResult(
                stage=OnboardingStage.AWAITING_CHOICE,
                status="in_progress",
                welcome_message=messages.build_new_user_welcome(),
                final_message=messages.render_capabilities_text(),
                actions=_base_actions(include_verification=True),
                is_verified=is_verified,
                capability_sections=capability_sections,
                route_hint="onboarding",
            ),
            onboarding_state,
        )

    if stage_enum is OnboardingStage.AWAITING_CHOICE:
        if is_verified or intent == "confirm_verified":
            onboarding_state["stage"] = OnboardingStage.VERIFIED_CAPABILITIES.value
            onboarding_state["verified_acknowledged"] = True
            intro = messages.build_verified_capabilities_intro(github_username)
            return (
                OnboardingFlowResult(
                    stage=OnboardingStage.VERIFIED_CAPABILITIES,
                    status="completed",
                    welcome_message=intro,
                    final_message=messages.render_capabilities_text(),
                    actions=_exploration_suggestions(),
                    is_verified=True,
                    capability_sections=capability_sections,
                    route_hint="onboarding",
                    handoff="github_toolkit",
                    next_tool="github_toolkit",
                ),
                onboarding_state,
            )

        if intent in {"skip", "explore", "help_verify"}:
            onboarding_state["stage"] = OnboardingStage.ENCOURAGE_VERIFICATION.value
            onboarding_state["reminders_sent"] = reminders_sent + 1
            reminder_message = messages.build_encourage_verification_message(reminders_sent)
            return (
                OnboardingFlowResult(
                    stage=OnboardingStage.ENCOURAGE_VERIFICATION,
                    status="in_progress",
                    welcome_message=reminder_message,
                    final_message=messages.render_capabilities_text(),
                    actions=_base_actions(include_verification=True) + _exploration_suggestions(),
                    is_verified=False,
                    capability_sections=capability_sections,
                    route_hint="onboarding",
                    handoff="github_toolkit",
                    next_tool="github_toolkit",
                    metadata={"reminders_sent": onboarding_state["reminders_sent"]},
                ),
                onboarding_state,
            )

        # Still waiting for a clear signal; restate verification pathway
        onboarding_state["stage"] = OnboardingStage.AWAITING_CHOICE.value
        return (
            OnboardingFlowResult(
                stage=OnboardingStage.AWAITING_CHOICE,
                status="in_progress",
                welcome_message=messages.build_new_user_welcome(),
                final_message=None,
                actions=_base_actions(include_verification=True),
                is_verified=False,
                capability_sections=capability_sections,
                route_hint="onboarding",
            ),
            onboarding_state,
        )

    if stage_enum is OnboardingStage.ENCOURAGE_VERIFICATION:
        if is_verified or intent == "confirm_verified":
            onboarding_state["stage"] = OnboardingStage.VERIFIED_CAPABILITIES.value
            onboarding_state["verified_acknowledged"] = True
            intro = messages.build_verified_capabilities_intro(github_username)
            return (
                OnboardingFlowResult(
                    stage=OnboardingStage.VERIFIED_CAPABILITIES,
                    status="completed",
                    welcome_message=intro,
                    final_message=messages.render_capabilities_text(),
                    actions=_exploration_suggestions(),
                    is_verified=True,
                    capability_sections=capability_sections,
                    route_hint="onboarding",
                    handoff="github_toolkit",
                    next_tool="github_toolkit",
                ),
                onboarding_state,
            )

        onboarding_state["reminders_sent"] = reminders_sent + 1
        reminder_message = messages.build_encourage_verification_message(reminders_sent)
        return (
            OnboardingFlowResult(
                stage=OnboardingStage.ENCOURAGE_VERIFICATION,
                status="in_progress",
                welcome_message=reminder_message,
                final_message=messages.render_capabilities_text(),
                actions=_base_actions(include_verification=True) + _exploration_suggestions(),
                is_verified=False,
                capability_sections=capability_sections,
                route_hint="onboarding",
                handoff="github_toolkit",
                next_tool="github_toolkit",
                metadata={"reminders_sent": onboarding_state["reminders_sent"]},
            ),
            onboarding_state,
        )

    if stage_enum is OnboardingStage.VERIFIED_CAPABILITIES:
        onboarding_state["stage"] = OnboardingStage.COMPLETED.value
        return (
            OnboardingFlowResult(
                stage=OnboardingStage.COMPLETED,
                status="completed",
                welcome_message=messages.build_verified_welcome(github_username),
                final_message=messages.render_capabilities_text(),
                actions=_exploration_suggestions(),
                is_verified=True,
                capability_sections=capability_sections,
                route_hint="onboarding",
                handoff="github_toolkit",
                next_tool="github_toolkit",
            ),
            onboarding_state,
        )

    # Completed state - short acknowledgement
    onboarding_state["stage"] = OnboardingStage.COMPLETED.value
    return (
        OnboardingFlowResult(
            stage=OnboardingStage.COMPLETED,
            status="completed",
            welcome_message=messages.build_verified_welcome(github_username),
            final_message=None,
            actions=_exploration_suggestions(),
            is_verified=is_verified,
            capability_sections=capability_sections,
            route_hint="onboarding",
            handoff="github_toolkit" if is_verified else None,
            next_tool="github_toolkit" if is_verified else None,
        ),
        onboarding_state,
    )
