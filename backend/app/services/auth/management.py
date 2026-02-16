import uuid
from datetime import datetime, timezone
from typing import Optional
from app.database.supabase.client import get_supabase_client
from app.models.database.supabase import User
import logging

logger = logging.getLogger(__name__)

async def get_or_create_user_by_discord(
    discord_id: str, display_name: str, discord_username: str, avatar_url: Optional[str]
) -> User:
    """
    Get or create a user by Discord ID.
    """
    supabase = get_supabase_client()
    existing_user_res = await supabase.table("users").select("*").eq("discord_id", discord_id).limit(1).execute()

    if existing_user_res.data:
        logger.info(f"Found existing user for Discord ID: {discord_id}")
        return User(**existing_user_res.data[0])

    # Create new user if not found
    logger.info(f"No user found for Discord ID: {discord_id}. Creating new user.")
    new_user_data = {
        "id": str(uuid.uuid4()),
        "discord_id": discord_id,
        "display_name": display_name,
        "discord_username": discord_username,
        "avatar_url": avatar_url,
        "preferred_languages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    insert_res = await supabase.table("users").insert(new_user_data).execute()
    if not insert_res.data:
        raise Exception("Failed to create new user in database.")

    logger.info(f"Successfully created new user with ID: {insert_res.data[0]['id']}")
    return User(**insert_res.data[0])

async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get user by their ID.
    """
    supabase = get_supabase_client()

    try:
        user_res = await supabase.table("users").select("*").eq("id", user_id).limit(1).execute()

        if user_res.data:
            return User(**user_res.data[0])
        return None
    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None

async def get_user_by_github_id(github_id: str) -> Optional[User]:
    """
    Get user by their GitHub ID.
    """
    supabase = get_supabase_client()

    try:
        user_res = await supabase.table("users").select("*").eq("github_id", github_id).limit(1).execute()

        if user_res.data:
            return User(**user_res.data[0])
        return None
    except Exception as e:
        logger.error(f"Error getting user by GitHub ID {github_id}: {e}")
        return None

async def update_user_profile(user_id: str, **updates) -> Optional[User]:
    """
    Update user profile data.
    """
    supabase = get_supabase_client()

    try:
        # Add updated_at timestamp
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()

        update_res = await supabase.table("users").update(updates).eq("id", user_id).execute()

        if update_res.data:
            logger.info(f"Successfully updated user {user_id}")
            return User(**update_res.data[0])
        return None
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return None
