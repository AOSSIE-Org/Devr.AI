import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
from app.agents.devrel.prompts.summarization_prompt import CONVERSATION_SUMMARY_PROMPT
from app.database.supabase.client import get_supabase_client

supabase = get_supabase_client()

def isoformat_or_none(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


logger = logging.getLogger(__name__)

# Configuration constants
SUMMARIZATION_THRESHOLD = 15
THREAD_TIMEOUT_HOURS = 1

async def check_summarization_needed(state: AgentState) -> Dict[str, Any]:
    """
    Check if summarization is needed and update interaction count
    """

    current_count = getattr(state, 'interaction_count', 0)
    new_count = current_count + 1

    # Check for timeout
    time_since_start = (datetime.now() - state.session_start_time)

    logger.info(f"Session {state.session_id}: "
                f"Messages: {len(state.messages)}, "
                f"Interaction count: {current_count} → {new_count}, "
                f"Threshold: {SUMMARIZATION_THRESHOLD}")

    updates = {
        "interaction_count": 1,
        "last_interaction_time": datetime.now()
    }

    if time_since_start > timedelta(hours=THREAD_TIMEOUT_HOURS):
        updates.update({
            "memory_timeout_reached": True,
            "summarization_needed": True
        })
        logger.info(f"Memory timeout reached for session {state.session_id}")
    elif new_count >= SUMMARIZATION_THRESHOLD:
        updates["summarization_needed"] = True
        logger.info(f"Summarization needed: {new_count} >= {SUMMARIZATION_THRESHOLD}")
    else:
        updates["summarization_needed"] = False
        logger.info(f"Summarization not needed: {new_count} < {SUMMARIZATION_THRESHOLD}")

    return updates

async def summarize_conversation_node(state: AgentState, llm) -> Dict[str, Any]:
    """
    Summarize the conversation and update the state
    """
    logger.info(f"Summarizing conversation for session {state.session_id}")

    try:
        current_count = state.interaction_count
        logger.info(f"Summarizing at interaction count: {current_count}")

        all_messages = state.messages

        if not all_messages:
            logger.warning("No messages to summarize")
            return {"summarization_needed": False}

        # Prepare conversation text
        conversation_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in all_messages
        ])

        existing_summary = state.conversation_summary
        if not existing_summary or existing_summary == "This is the beginning of our conversation.":
            existing_summary = "No previous summary - this is the start of our conversation tracking."

        user_profile_text = str(state.user_profile) if state.user_profile else "No user profile."
        topics_context = f"Previous topics: {', '.join(state.key_topics)}" if state.key_topics else "No previous topics."

        prompt = CONVERSATION_SUMMARY_PROMPT.format(
            existing_summary=existing_summary,
            recent_conversation=conversation_text,
            user_profile=user_profile_text
        )

        prompt = prompt + f"\n\nPrevious topics discussed: {topics_context}"

        logger.info(f"Generating summary with {len(all_messages)} messages, "
                    f"conversation text length: {len(conversation_text)}")

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        new_summary = response.content.strip()

        new_topics = await _extract_key_topics(new_summary, llm)

        logger.info(f"Conversation summarized successfully for session {state.session_id}")

        return {
            "conversation_summary": new_summary,
            "interaction_count": -current_count,
            "summarization_needed": False,
            "key_topics": new_topics
        }

    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return {
            "errors": [f"Summarization error: {str(e)}"],
            "summarization_needed": False
        }

async def _extract_key_topics(summary: str, llm) -> list[str]:
    """Extract key topics from the conversation summary"""
    try:
        topic_prompt = f"""Extract the key technical topics from this conversation summary.
        Return only topic names separated by commas.
        
        Summary: {summary}
        
        Topics:"""

        response = await llm.ainvoke([HumanMessage(content=topic_prompt)])
        topics_text = response.content.strip()

        topics = [topic.strip() for topic in topics_text.split(',') if topic.strip()]
        return topics[:5]  # Limiting to 5 topics

    except Exception as e:
        logger.error(f"Error extracting topics: {str(e)}")
        return []

async def store_summary_to_database(state: AgentState) -> None:
    """Store the summary in Supabase database"""
    logger.info(f"Storing summary for session {state.session_id} into conversation_context")

    try:
        # Validate required fields
        if not state.user_id or not state.platform:
            logger.error(f"Missing required fields: user_id={state.user_id}, platform={state.platform}")
            return

        user_uuid = state.context.get("user_uuid")

        if not user_uuid:
            platform_id = state.user_id
            platform_column = f"{state.platform}_id"

            user_response = await supabase.table("users").select("id").eq(platform_column, platform_id).limit(1).execute()

            if not user_response.data:
                logger.error(f"User with {platform_column} '{platform_id}' not found in users table.")
                return

            user_uuid = user_response.data[0]['id']
            logger.info(f"Found user UUID: {user_uuid} for {platform_column}: {platform_id}")
        else:
            logger.info(f"Using cached user UUID from context: {user_uuid}")

        # Record to insert/update
        record = {
            "user_id": user_uuid,
            "conversation_summary": state.conversation_summary,
            "key_topics": state.key_topics,
            "total_interactions": state.interaction_count,
            "session_start_time": isoformat_or_none(state.session_start_time),
            "session_end_time": isoformat_or_none(datetime.now()),
        }

        # Upsert based on the user_id to ensure one summary per user
        response = await supabase.table("conversation_context").upsert(record, on_conflict="user_id").execute()

        # Checks
        if response.data and len(response.data) > 0:
            logger.info(f"✅ Summary stored successfully for session {state.session_id}")
        else:
            logger.error(f"❌ Supabase upsert failed for session {state.session_id}: {response}")

    except Exception as e:
        logger.error(f"Unexpected error while storing summary: {str(e)}")
