DEVREL_TRIAGE_PROMPT = """Analyze this message to determine if it needs DevRel assistance. 
Be EXTREMELY STRICT and CONSERVATIVE - the DevRel agent should only be triggered in very specific circumstances.

Message: {message}

Context: {context}

STRICT ACTIVATION RULES - DevRel agent should ONLY be triggered if:

1. EXPLICIT BOT MENTION/TAG (highest priority):
   - User explicitly mentions the DevRel AI bot (e.g., "@Devr.AI", "hey bot", 
     "can you help", "@assistant")
   - User directly addresses the AI assistant with phrases like "AI", "bot", 
     "assistant", "help me"
   - User uses command-like language: "bot, can you...", "assistant, please..."

2. DIRECT PROJECT QUESTIONS (only if clearly related to THIS specific repository/project):
   - Setup/installation questions: "How do I set up the development environment?"
   - Build/compilation errors: "I'm getting a build error", "compilation failed"
   - Contribution process: "How do I contribute?", "How do I submit a PR?"
   - Repository-specific technical issues: "This API endpoint isn't working"
   - Documentation requests about THIS project: "Where is the API documentation?"

IGNORE COMPLETELY (always return false):
- General chatter between users: "Hey, how's it going?", "What's for lunch?"
- Greetings without bot mention: "Hi everyone", "Good morning"
- General programming questions not specific to this project: "How do I use React?"
- Conversations between other users that don't mention the bot
- Off-topic discussions: weather, personal conversations, unrelated topics
- Vague statements without clear questions: "This is cool", "Nice work"
- General complaints without specific technical issues: "This is frustrating"
- General questions that could be answered by anyone: "What time is it?", "How's the weather?"
- Questions about other projects or technologies not related to this repository
- Social conversations, jokes, or casual banter
- Questions that don't require technical assistance

CRITICAL: If the message is general conversation, casual chat, or doesn't explicitly 
involve the bot OR a specific question about THIS project/repository, return needs_devrel: false.

BE CONSERVATIVE: When in doubt, return false. It's better to miss a few legitimate requests 
than to respond to inappropriate messages.

Respond ONLY with JSON:
{{
    "needs_devrel": true/false,
    "priority": "high|medium|low",
    "reasoning": "brief explanation of decision"
}}

STRICT Examples:
- "How do I contribute?" → {{"needs_devrel": true, "priority": "high", 
  "reasoning": "Direct contribution question"}}
- "Hey @Devr.AI, can you help me?" → {{"needs_devrel": true, "priority": "high", 
  "reasoning": "Explicit bot mention"}}
- "I'm getting a build error in this project" → {{"needs_devrel": true, "priority": "high", 
  "reasoning": "Project-specific technical issue"}}
- "What's for lunch?" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "General chatter, not project-related"}}
- "Hi everyone" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "General greeting without bot mention"}}
- "How do I use React?" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "General programming question, not project-specific"}}
- "Nice work on this feature" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "General comment, no question or bot mention"}}
- "That's frustrating" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "Vague complaint without specific issue"}}
- "What time is it?" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "General question not requiring technical assistance"}}
- "How's the weather?" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "Off-topic question unrelated to project"}}
- "This is a great project" → {{"needs_devrel": false, "priority": "low", 
  "reasoning": "General compliment, no question or bot mention"}}
"""
