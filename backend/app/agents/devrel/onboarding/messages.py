"""Shared onboarding messaging primitives used across channels."""
from __future__ import annotations

from typing import Dict, List, Optional

# Structured capability sections pulled from design docs so UI and LLM share copy
CAPABILITY_SECTIONS: List[Dict[str, List[str]]] = [
    {
        "title": "Explore Our Projects",
        "examples": [
            "Show me our most active repositories.",
            "Give me an overview of the 'Devr.AI-backend' repo.",
        ],
    },
    {
        "title": "Find Ways to Contribute",
        "examples": [
            "Are there any 'good first issues' available?",
            "Find issues with the 'bug' label.",
        ],
    },
    {
        "title": "Answer Project Questions",
        "examples": [
            "How do I set up the local development environment?",
            "What's the process for submitting a pull request?",
        ],
    },
]

CAPABILITIES_INTRO_TEXT = (
    "You're all set! As the Devr.AI assistant, my main purpose is to help you "
    "navigate and contribute to our projects. Here's a look at what you can ask "
    "me to do."
)
CAPABILITIES_OUTRO_TEXT = "Feel free to ask me anything related to the project. What's on your mind?"


def render_capabilities_text() -> str:
    """Render the capabilities message as plain text for chat responses."""
    lines: List[str] = [CAPABILITIES_INTRO_TEXT, ""]
    for section in CAPABILITY_SECTIONS:
        lines.append(f"{section['title']}:")
        for example in section["examples"]:
            lines.append(f"- \"{example}\"")
        lines.append("")
    lines.append(CAPABILITIES_OUTRO_TEXT)
    return "\n".join(lines).strip()


def build_new_user_welcome() -> str:
    """Welcome copy when verification is still pending."""
    return (
        "👋 Welcome to the Devr.AI community! I'm here to help you get started on your contributor journey.\n\n"
        "To give you the best recommendations for repositories and issues, I first need to link your GitHub account. "
        "This one-time step helps me align tasks with your profile.\n\n"
        "Here's how to verify:\n"
        "- Run `/verify_github` to start verification right away.\n"
        "- Use `/verification_status` to see if you're already linked.\n"
        "- Use `/help` anytime to explore everything I can assist with.\n\n"
        "Would you like to verify your GitHub account now or skip this step for now? You can always do it later."
    )


def build_verified_welcome(github_username: Optional[str] = None) -> str:
    """Welcome copy for returning verified contributors."""
    greeting = "👋 Welcome back to the Devr.AI community!"
    if github_username:
        greeting += f" I see `{github_username}` is already linked, which is great."
    else:
        greeting += " I see your GitHub account is already verified, which is great."
    return (
        f"{greeting}\n\nHow can I help you get started today? Ask me for repository overviews, issues to work on, or project guidance whenever you're ready."
    )


def build_encourage_verification_message(reminder_count: int = 0) -> str:
    """Reminder copy for users who haven't verified yet but want to explore."""
    reminder_prefix = "Quick reminder" if reminder_count else "No worries"
    return (
        f"{reminder_prefix} — linking your GitHub unlocks personalized suggestions. "
        "Run `/verify_github` when you're ready, and `/verification_status` to check progress.\n\n"
        "While you set that up, I can still show you what's happening across the organization. "
        "Ask for repository highlights, open issues, or anything else you're curious about."
    )


def build_verified_capabilities_intro(github_username: Optional[str] = None) -> str:
    """Intro text shown right before the capability menu for verified users."""
    if github_username:
        return (
            f"Awesome — `{github_username}` is linked! You're all set to explore. "
            "Here's a quick menu of what I can help you with right away."
        )
    return (
        "Great! Your GitHub account is connected and I'm ready to tailor suggestions. "
        "Here are the top things I can help with."
    )
