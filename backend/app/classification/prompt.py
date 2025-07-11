DEVREL_TRIAGE_PROMPT = """Analyze this message to determine if it needs DevRel assistance. 
Be VERY STRICT - the DevRel agent should only be triggered in specific circumstances.

Message: {message}

Context: {context}

STRICT ACTIVATION RULES - DevRel agent should ONLY be triggered if:

1. EXPLICIT BOT MENTION/TAG:
   - User explicitly mentions the DevRel AI bot (e.g., "@Devr.AI", "hey bot", 
     "can you help", "@assistant")
   - User directly addresses the AI assistant with phrases like "AI", "bot", 
     "assistant", "help me"

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

CRITICAL: If the message is general conversation, casual chat, or doesn't explicitly 
involve the bot OR a specific question about THIS project/repository, return needs_devrel: false.

Respond ONLY with JSON:
{{
    "needs_devrel": true/false,
    "priority": "high|medium|low",
    "reasoning": "brief explanation of decision"
}}

STRICT Examples:
- "How do I contribute?" → {{"needs_devrel": true, "priority": "high", 
  "reasoning": "Direct contribution question"}}
- "Hey @Devr.AI, can you help me?" → {{"needs_devrel": true, "priority": "medium", 
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
"""
