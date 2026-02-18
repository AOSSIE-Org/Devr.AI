CONVERSATION_SUMMARY_PROMPT = """You are a DevRel assistant. Create a concise, structured summary of this conversation.

EXISTING SUMMARY:
{existing_summary}

RECENT CONVERSATION:
{recent_conversation}

USER PROFILE:
{user_profile}

SUMMARY STRUCTURE - Use these sections:

**User Context:**
- Experience level (new contributor, experienced dev, maintainer, etc.)
- Primary interests/focus areas
- Platform/tech stack they're using

**Interaction History:**
- What questions they've asked
- What issues/problems they've encountered
- What help they've received

**Current Status:**
- What they're currently working on
- Any pending issues or blockers
- Next steps or goals mentioned

**Key Preferences/Notes:**
- Communication style (prefers detailed/brief responses)
- Timezone/availability if mentioned
- Special considerations

MERGING INSTRUCTIONS:
- If existing summary exists: Update it with new info, don't just append
- Remove outdated information (e.g., "currently blocked" if now resolved)
- Keep most recent context prioritized
- Consolidate duplicate information

KEEP IT CONCISE:
- Maximum 250 words
- Focus on actionable context for future interactions
- Prioritize recent and relevant information
- Remove unnecessary conversational filler

EXAMPLES:

Good Summary:
**User Context:** New open-source contributor, learning Python. Using Windows 10.
**Interaction History:** Asked about setup process (resolved), contribution guidelines (provided), now working on issue #45.
**Current Status:** Implementing feature for authentication module. Stuck on JWT configuration.
**Key Preferences:** Prefers step-by-step instructions with code examples.

Bad Summary:
User said hello. Then asked about contributing. We talked about setup. They're working on something. They seem nice.

Create a NEW summary combining existing and recent conversation:"""