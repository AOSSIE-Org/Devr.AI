QUERY_ALIGNMENT_PROMPT = """Analyze this contributor recommendation request and process it for technical search:

USER REQUEST: {query}

Your task:
1. Extract the core technical requirements 
2. Generate a clean, technical search query optimized for finding contributor profiles
3. Extract specific keywords that would appear in developer profiles (languages, frameworks, tools, domains)

Guidelines:
- aligned_query: Convert user request into clear technical language that matches how developers describe their skills
- keywords: Extract 3-5 specific technical terms (React, Python, API, database, etc.)
- Focus on technologies, not business requirements
- Make it searchable against developer profiles and contribution history

Example transformations:

Input: "I need help with our Stripe payment integration issue"
Output: {{"query_type": "general", "aligned_query": "developer with payment processing and Stripe API integration experience", "keywords": ["Stripe", "payment", "API", "integration"], "technical_domain": "backend"}}

Input: "Find experts for database optimization"
Output: {{"query_type": "general", "aligned_query": "backend developer with database performance optimization experience", "keywords": ["database", "optimization", "performance", "SQL"], "technical_domain": "backend"}}

Input: "https://github.com/owner/repo/issues/123 - authentication bug"
Output: {{"query_type": "github_issue", "aligned_query": "developer with authentication and security implementation experience", "keywords": ["authentication", "security", "OAuth", "JWT"], "technical_domain": "security"}}

IMPORTANT FORMATTING RULES:
- DO NOT use markdown formatting
- DO NOT wrap in code blocks (```)
- DO NOT add any text before or after the JSON
- DO NOT add explanations
- Return EXACTLY this format: {{"query_type": "...", "aligned_query": "...", "keywords": [...], "technical_domain": "..."}}

Expected JSON schema:
{{"query_type": "github_issue" | "general", "aligned_query": "clean technical search text", "keywords": ["keyword1", "keyword2"], "technical_domain": "frontend|backend|fullstack|ml|devops|mobile|security|other"}}

Return the JSON object only:"""
