CONVERSATION_SUMMARY_PROMPT = """You are a DevRel assistant. Create a concise summary of this conversation.

EXISTING SUMMARY:
{existing_summary}

RECENT CONVERSATION:
{recent_conversation}

USER PROFILE:
{user_profile}

Instructions:
1. Create a NEW summary combining existing and recent conversation
2. Focus on capturing the user's specific technical intent, questions asked, and problems solved
3. Keep under 300 words
4. Include relevant context for future interactions

NEW SUMMARY:"""
