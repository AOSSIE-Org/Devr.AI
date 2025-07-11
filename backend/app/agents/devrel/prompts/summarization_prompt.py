CONVERSATION_SUMMARY_PROMPT = """You are a DevRel assistant. Create a concise summary 
of this conversation for future context.

EXISTING SUMMARY: {existing_summary}
RECENT CONVERSATION: {recent_conversation}
USER PROFILE: {user_profile}

SUMMARY FOCUS:
1. User's technical background and experience level
2. Specific problems or challenges they're facing
3. Topics of interest and areas they're exploring
4. Key solutions or resources provided
5. Follow-up items or ongoing assistance needed

REQUIREMENTS:
- Combine existing and recent conversation into NEW summary
- Keep under 300 words for efficiency
- Include relevant context for future interactions
- Focus on actionable insights about the user's needs

NEW SUMMARY:"""
