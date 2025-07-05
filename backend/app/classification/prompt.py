DEVREL_TRIAGE_PROMPT = """Analyze this message to determine if it needs DevRel assistance.

Message: {message}

Context: {context}

DevRel handles:
- Technical questions about projects/APIs
- Developer onboarding and support
- Bug reports and feature requests  
- Community discussions about development
- Documentation requests
- General developer experience questions

Respond ONLY with JSON:
{{
    "needs_devrel": true/false,
    "priority": "high|medium|low",
    "reasoning": "brief explanation"
}}

Examples:
- "How do I contribute?" → {{"needs_devrel": true, "priority": "high", "reasoning": "Onboarding question"}}
- "What's for lunch?" → {{"needs_devrel": false, "priority": "low", "reasoning": "Not development related"}}
- "API is throwing errors" → {{"needs_devrel": true, "priority": "high", "reasoning": "Technical support needed"}}
"""
