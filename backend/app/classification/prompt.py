DEVREL_TRIAGE_PROMPT = """Analyze this message to determine if it needs DevRel assistance.

Message: {message}

Context: {context}

STRICT ACTIVATION RULES - DevRel responds ONLY when:

1. The bot is explicitly tagged or mentioned (e.g., @devr, @bot, mentions the bot by name)
   - Even if off-topic, return true so bot can acknowledge and redirect
   - Mark priority as "low" if question is off-topic
   
2. OR the message is a DIRECT QUESTION (contains ?, asks how/what/where/when/why) specifically about THIS PROJECT:
   - Project/repository setup, installation, or configuration
   - Contribution guidelines, process, or how to get started
   - Specific technical errors, bugs, or issues related to the project
   - Repository documentation, resources, or where to find information
   - How to use project APIs, features, or tools
   - Development environment setup or tooling

CRITICAL: IGNORE IF NOT RELEVANT (return needs_devrel: false) for:
- General greetings, small talk, or casual conversation ("Hey!", "Good morning", "How's everyone?")
- Thank you messages or acknowledgments without follow-up questions ("Thanks!", "Got it", "Appreciate it")
- Statements or updates without asking for help ("I'm working on X", "I installed Y", "Setup is done")
- Conversations between other users where the bot is not mentioned or needed
- Off-topic discussions unrelated to this specific project or repository
- Vague questions without THIS PROJECT'S context ("How do I code?", "What's Python?", "How do I learn programming?")
  * KEY: "How do I learn Python?" (general) → false
  * BUT: "How do I learn to setup this bot?" (project-specific) → true
- Developer discussions that don't explicitly request assistance
- Reactions, emojis, or single-word responses
- Questions already being answered by other community members (unless bot is specifically asked)

DECISION CRITERIA:
- If unsure → return false (err on the side of NOT responding)
- Statements without clear questions → return false
- Questions not related to THIS PROJECT → return false
- Bot tagged but off-topic → return true with priority "low" (so bot can acknowledge and redirect)
- Bot tagged with project question → return true with priority "high"

Respond ONLY with JSON:
{{
    "needs_devrel": true/false,
    "priority": "high|medium|low",
    "reasoning": "brief explanation"
}}

EXAMPLES:

 SHOULD RESPOND (needs_devrel: true):
- "How do I set up the development environment?" 
  → {{"needs_devrel": true, "priority": "high", "reasoning": "Direct setup question"}}

- "@devr what's the contribution process?" 
  → {{"needs_devrel": true, "priority": "high", "reasoning": "Bot tagged with project-specific question"}}

- "@devr what's for lunch?"
  → {{"needs_devrel": true, "priority": "low", "reasoning": "Bot tagged but off-topic, should acknowledge politely"}}

- "Where can I find the API documentation?" 
  → {{"needs_devrel": true, "priority": "medium", "reasoning": "Documentation question"}}

- "I'm getting a 'module not found' error when running npm install. How do I fix this?" 
  → {{"needs_devrel": true, "priority": "high", "reasoning": "Technical issue with clear question"}}

- "Can someone explain how the authentication flow works in this repo?" 
  → {{"needs_devrel": true, "priority": "medium", "reasoning": "Project-specific technical question"}}

 SHOULD IGNORE (needs_devrel: false):
- "Hey everyone, good morning!" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "General greeting, not project-related"}}

- "What's for lunch?" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "Off-topic, not development related"}}

- "Thanks for the help!" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "Acknowledgment without question"}}

- "I'm setting up the project right now" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "Statement without asking for help"}}

- "The API is throwing errors" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "Statement, not a question - user didn't ask for help"}}

- "How do I learn Python?" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "General programming question, not project-specific"}}

- "User1: How do I contribute? User2: Check the CONTRIBUTING.md file" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "Question being answered by community, bot not needed"}}

- "lol that's funny" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "Casual chat, not a question"}}

- "👍" 
  → {{"needs_devrel": false, "priority": "low", "reasoning": "Reaction emoji, no content"}}
"""