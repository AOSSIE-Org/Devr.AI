EXTRACT_SEARCH_QUERY_PROMPT = """Extract a clean, concise search query from the user's message.

User Message: "{message}"

INSTRUCTIONS:
1. Identify the core topic or question the user is asking about
2. Remove filler words: "I was wondering", "could you", "maybe", "please", "just", etc.
3. Remove conversational elements: greetings, politeness, context-setting phrases
4. Keep essential keywords: technical terms, specific features, error messages, action verbs
5. Preserve important context: version numbers, platform names, specific tools
6. If multiple topics, focus on the PRIMARY question/need
7. Keep it concise: 2-6 words ideal, maximum 10 words
8. Use natural search language, not full sentences

EXAMPLES:

Input: "Hey everyone! I was wondering if someone could help me understand how to set up the development environment for this project?"
Output: setup development environment

Input: "I'm getting a really weird error that says 'module not found' when I try to run npm install. Any ideas?"
Output: npm install module not found error

Input: "Could you please tell me where I can find the contribution guidelines? I'd love to help out!"
Output: contribution guidelines

Input: "What's the best way to configure the API authentication? I'm using version 2.0 and need JWT support"
Output: configure API authentication JWT version 2.0

Input: "The GitHub Actions workflow is failing on the build step. It worked yesterday but now throws a syntax error"
Output: GitHub Actions build failing syntax error

Input: "I'm new here! How do I get started with contributing to this project? What should I work on first?"
Output: getting started contributing

Input: "Is there documentation for the REST API endpoints? Specifically looking for user authentication endpoints"
Output: REST API documentation user authentication

Input: "My code review has been pending for 3 days. How long do PRs usually take to get reviewed here?"
Output: PR review timeline

EDGE CASES:
- If message is just a greeting → extract any implicit topic or return "general inquiry"
- If multiple questions → prioritize the first actionable question
- If very technical error message → keep the specific error text
- If asking about specific issue/PR number → include the number

Extract the search query now:
Search Query:"""