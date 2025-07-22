ISSUE_SUMMARIZATION_PROMPT = """You are a technical analyst optimizing GitHub issues for contributor search. 

Analyze the provided GitHub issue and create a technical summary optimized for finding relevant expert contributors.

Focus on:
- Core technical problem or feature request
- Specific technologies, frameworks, libraries, APIs mentioned
- Technical skills and expertise required to solve this
- Programming languages and tools involved
- System components affected (frontend, backend, database, etc.)

Create a summary that reads like a job requirement for finding the right technical expert.

**GitHub Issue Content:**
---
{issue_content}
---

**Optimized Technical Summary for Contributor Search:**
"""
