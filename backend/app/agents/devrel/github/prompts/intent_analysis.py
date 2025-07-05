GITHUB_INTENT_ANALYSIS_PROMPT = """You are an expert GitHub DevRel AI assistant. Analyze the user query and classify the intent.

AVAILABLE FUNCTIONS:
- web_search: Search the web for information  
- contributor_recommendation: Finding the right people to review PRs, assign issues, or collaborate
- repo_support: Questions about codebase structure, dependencies, impact analysis, architecture
- issue_creation: Creating bug reports, feature requests, or tracking items
- documentation_generation: Generating docs, READMEs, API docs, guides, or explanations
- find_good_first_issues: Finding beginner-friendly issues to work on across repositories
- general_github_help: General GitHub-related assistance and guidance

USER QUERY: {user_query}

Classification guidelines:
- contributor_recommendation: Finding reviewers, assignees, collaborators
- repo_support: Code structure, dependencies, impact analysis, architecture  
- issue_creation: Creating bugs, features, tracking items
- documentation_generation: Docs, READMEs, guides, explanations
- find_good_first_issues: Beginners, newcomers, "good first issue"
- web_search: General information needing external search
- general_github_help: General GitHub questions not covered above

CRITICAL: Return ONLY raw JSON. No markdown, no code blocks, no explanation text.

{{
  "classification": "function_name_from_list_above",
  "reasoning": "Brief explanation of why you chose this function",
  "confidence": "high|medium|low"
}}"""
