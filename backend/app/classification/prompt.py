DEVREL_TRIAGE_PROMPT = """Analyze this message to determine if it needs DevRel assistance.

Message: {message}

Context: {context}

CRITICAL INSTRUCTIONS:
The DevRel Agent is a SPECIALIZED technical assistant. It must NOT interfere in normal human conversation.
It should ONLY be activated if one of the following conditions is met:

1. **DIRECT MENTION**: The user explicitly tags or names the bot (e.g., "@Devr.AI", "bot", "assistant").
   - Action: `needs_devrel: true`
   - Priority: `high`

2. **TECHNICAL SUPPORT**: The user asks a specific technical question about the project, code, API, or installation.
   - Example: "How do I set up the environment?", "I'm getting a build error", "Where is the API doc?"
   - Action: `needs_devrel: true`
   - Priority: `medium`

3. **CONTRIBUTION/COMMUNITY**: The user asks about contributing, PRs, issues, or community guidelines.
   - Action: `needs_devrel: true`
   - Priority: `medium`

**IGNORE (needs_devrel: false)**:
- General greetings ("Hi", "Hello", "Good morning") unless tagged.
- Social chatter ("How are you?", "This is cool", "lol") unless tagged.
- Discussions between users that don't involve the project specifics.
- Vague statements without a clear question.

Respond ONLY with JSON:
{{
    "needs_devrel": true/false,
    "priority": "high|medium|low",
    "reasoning": "Brief explanation of why it fits/excludes criteria"
}}

Examples:
- "Hi everyone!" → {{"needs_devrel": false, "priority": "low", "reasoning": "General greeting, no tag"}}
- "@Devr.AI Hi!" → {{"needs_devrel": true, "priority": "high", "reasoning": "Direct mention"}}
- "I'm getting a 500 error on /api/login" → {{"needs_devrel": true, "priority": "medium", "reasoning": "Technical support"}}
- "I think we should use React" → {{"needs_devrel": false, "priority": "low", "reasoning": "Opinion"}}
- "How do I submit a PR?" → {{"needs_devrel": true, "priority": "medium", "reasoning": "Contribution question"}}
"""
