import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from app.database.supabase.client import get_supabase_client

logger = logging.getLogger(__name__)
supabase = get_supabase_client()


async def ensure_user_exists(
    user_id: str,
    platform: str,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
    avatar_url: Optional[str] = None
) -> Optional[str]:
    """
    Ensure a user exists in the database. If not, create them.
    Returns the user's UUID, or None if an error occurs.

    Args:
        user_id: Platform-specific user ID (e.g., discord_id, slack_id)
        platform: Platform name (discord, slack, github)
        username: Platform username
        display_name: Display name for the user
        avatar_url: Avatar URL

    Returns:
        User UUID as string, or None on error
    """
    try:
        platform_id_column = f"{platform}_id"
        platform_username_column = f"{platform}_username"

        # Check if user exists
        response = await supabase.table("users").select("id").eq(platform_id_column, user_id).limit(1).execute()

        if response.data:
            user_uuid = response.data[0]['id']
            logger.info(f"User found: {user_uuid} for {platform_id_column}: {user_id}")

            # Update last_active timestamp
            last_active_column = f"last_active_{platform}"
            await supabase.table("users").update({
                last_active_column: datetime.now().isoformat()
            }).eq("id", user_uuid).execute()

            return user_uuid

        # User doesn't exist, create new user
        logger.info(f"Creating new user for {platform_id_column}: {user_id}")

        new_user = {
            "id": str(uuid.uuid4()),
            platform_id_column: user_id,
            "display_name": display_name or username or f"{platform}_user_{user_id[:8]}",
        }

        if username:
            new_user[platform_username_column] = username
        if avatar_url:
            new_user["avatar_url"] = avatar_url

        # Set last_active timestamp
        last_active_column = f"last_active_{platform}"
        new_user[last_active_column] = datetime.now().isoformat()

        insert_response = await supabase.table("users").insert(new_user).execute()

        if insert_response.data:
            user_uuid = insert_response.data[0]['id']
            logger.info(f"User created successfully: {user_uuid}")
            return user_uuid
        else:
            logger.error(f"Failed to create user: {insert_response}")
            return None

    except Exception as e:
        logger.error(f"Error ensuring user exists: {str(e)}")
        return None


async def store_interaction(
    user_uuid: str,
    platform: str,
    platform_specific_id: str,
    channel_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    content: Optional[str] = None,
    interaction_type: Optional[str] = None,
    intent_classification: Optional[str] = None,
    topics_discussed: Optional[list] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Store an interaction in the database.

    Args:
        user_uuid: User's UUID from users table
        platform: Platform name (discord, slack, github)
        platform_specific_id: Platform-specific message/interaction ID
        channel_id: Channel ID where interaction occurred
        thread_id: Thread ID where interaction occurred
        content: Content of the interaction
        interaction_type: Type of interaction (message, comment, pr, etc.)
        intent_classification: Classification of user intent
        topics_discussed: List of topics discussed
        metadata: Additional metadata

    Returns:
        True if successful, False otherwise
    """
    try:
        interaction_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_uuid,
            "platform": platform,
            "platform_specific_id": platform_specific_id,
        }

        if channel_id:
            interaction_data["channel_id"] = channel_id
        if thread_id:
            interaction_data["thread_id"] = thread_id
        if content:
            interaction_data["content"] = content
        if interaction_type:
            interaction_data["interaction_type"] = interaction_type
        if intent_classification:
            interaction_data["intent_classification"] = intent_classification
        if topics_discussed:
            interaction_data["topics_discussed"] = topics_discussed
        if metadata:
            interaction_data["metadata"] = metadata

        response = await supabase.table("interactions").insert(interaction_data).execute()

        if response.data:
            logger.info(f"Interaction stored successfully for user {user_uuid}")

            # Increment user's total_interactions_count
            # First get the current count
            user_response = await supabase.table("users").select("total_interactions_count").eq("id", user_uuid).limit(1).execute()
            if user_response.data:
                current_count = user_response.data[0].get("total_interactions_count", 0)
                await supabase.table("users").update({
                    "total_interactions_count": current_count + 1
                }).eq("id", user_uuid).execute()

            return True
        else:
            logger.error(f"Failed to store interaction: {response}")
            return False

    except Exception as e:
        logger.error(f"Error storing interaction: {str(e)}")
        return False


async def get_conversation_context(user_uuid: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve conversation context for a user.

    Args:
        user_uuid: User's UUID from users table

    Returns:
        Dictionary containing conversation context, or None if not found
    """
    try:
        response = await supabase.table("conversation_context").select("*").eq("user_id", user_uuid).limit(1).execute()

        if response.data:
            context = response.data[0]
            logger.info(f"Retrieved conversation context for user {user_uuid}")
            return {
                "conversation_summary": context.get("conversation_summary"),
                "key_topics": context.get("key_topics", []),
                "total_interactions": context.get("total_interactions", 0),
                "session_start_time": context.get("session_start_time"),
                "session_end_time": context.get("session_end_time"),
            }
        else:
            logger.info(f"No conversation context found for user {user_uuid}")
            return None

    except Exception as e:
        logger.error(f"Error retrieving conversation context: {str(e)}")
        return None
