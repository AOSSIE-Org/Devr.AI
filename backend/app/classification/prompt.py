DEVREL_TRIAGE_PROMPT = """
Analyze this message to determine if it needs DevRel assistance.

Message: {message}

Context: {context}

DevRel should be triggered ONLY if:
- The user explicitly mentions or tags the DevRel AI bot (e.g., "@Devr.AI", "@devrel", etc.)
- The message is a direct question about setting up the project, contributing, build/runtime errors, or anything clearly about this repository’s development.
- The user asks about documentation, onboarding, or GitHub issues/PRs in this repo.

DO NOT trigger DevRel for:
- General conversation, greetings, or unrelated chat
- Messages between users that do NOT mention the bot

Respond ONLY with JSON:
{
    "needs_devrel": true/false,
    "priority": "high|medium|low",
    "reasoning": "brief explanation"
}

Examples:
- "@Devr.AI how do I build this?" → {"needs_devrel": true, "priority": "high", "reasoning": "Explicitly tagged bot for setup help"}
- "Hi everyone!" → {"needs_devrel": false, "priority": "low", "reasoning": "General greeting"}
- "I’m getting an error installing requirements.txt" → {"needs_devrel": true, "priority": "high", "reasoning": "Direct technical setup issue"}
- "Who wants coffee?" → {"needs_devrel": false, "priority": "low", "reasoning": "Not development related"}
"""
