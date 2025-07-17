EXTRACT_SEARCH_QUERY_PROMPT = """Extract the most effective search query from the user message.

User Message: "{message}"

GUIDELINES:
- Focus on the main topic, key terms, and specific questions
- Remove conversational filler ("I was wondering", "Can you help me")
- Include technical terms, tool names, and specific concepts
- Keep it concise but comprehensive (2-8 key words/phrases)
- Preserve important context that affects the search

Examples:
- "I'm having trouble setting up Docker" → "Docker setup troubleshooting"
- "Can you help me understand how React hooks work?" → "React hooks tutorial guide"
- "What's the best way to deploy to AWS?" → "AWS deployment best practices"

Search Query:"""
