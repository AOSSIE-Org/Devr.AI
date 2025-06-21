import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from app.db.supabase.supabase_client import get_supabase_client
from app.model.supabase.models import User
import logging

logger = logging.getLogger(__name__)

# session_id -> (discord_id, expiry_time)
_verification_sessions: Dict[str, Tuple[str, datetime]] = {}

SESSION_EXPIRY_MINUTES = 5

async def get_or_create_user_by_discord(discord_id: str, display_name: str, discord_username: str, avatar_url: Optional[str]) -> User:
    """
    Get or create a user by Discord ID.
    """
    supabase = get_supabase_client()
    existing_user_res = await supabase.table("users").select("*").eq("discord_id", discord_id).limit(1).execute()

    if existing_user_res.data:
        logger.info(f"Found existing user for Discord ID: {discord_id}")
        return User(**existing_user_res.data[0])
    else:
        logger.info(f"No user found for Discord ID: {discord_id}. Creating new user.")
        new_user_data = {
            "id": str(uuid.uuid4()),
            "discord_id": discord_id,
            "display_name": display_name,
            "discord_username": discord_username,
            "avatar_url": avatar_url,
            "preferred_languages": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        insert_res = await supabase.table("users").insert(new_user_data).execute()
        if not insert_res.data:
            raise Exception("Failed to create new user in database.")
        return User(**insert_res.data[0])

def _cleanup_expired_sessions():
    """
    Remove expired verification sessions.
    """
    current_time = datetime.now()
    expired_sessions = [
        session_id for session_id, (discord_id, expiry_time) in _verification_sessions.items()
        if current_time > expiry_time
    ]

    for session_id in expired_sessions:
        discord_id, _ = _verification_sessions[session_id]
        del _verification_sessions[session_id]
        logger.info(f"Cleaned up expired verification session {session_id} for Discord user {discord_id}")

    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired verification sessions")

async def create_verification_session(discord_id: str) -> Optional[str]:
    """
    Create a verification session with expiry and return session ID.
    """
    supabase = get_supabase_client()

    _cleanup_expired_sessions()

    token = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    expiry_time = datetime.now() + timedelta(minutes=SESSION_EXPIRY_MINUTES)

    try:
        update_res = await supabase.table("users").update({
            "verification_token": token,
            "verification_token_expires_at": expiry_time.isoformat(),
            "updated_at": datetime.now().isoformat()
        }).eq("discord_id", discord_id).execute()

        if update_res.data:
            _verification_sessions[session_id] = (discord_id, expiry_time)
            logger.info(
                f"Created verification session {session_id} for Discord user {discord_id}, expires at {expiry_time}")
            return session_id
        else:
            logger.error(f"Failed to set verification token for Discord ID: {discord_id}. User not found.")
            return None
    except Exception as e:
        logger.error(f"Error creating verification session for Discord ID {discord_id}: {str(e)}")
        return None

async def find_user_by_session_and_verify(session_id: str, github_id: str, github_username: str, email: Optional[str]) -> Optional[User]:
    """
    Find and verify user using session ID with expiry validation.
    """
    supabase = get_supabase_client()

    _cleanup_expired_sessions()

    try:
        session_data = _verification_sessions.get(session_id)
        if not session_data:
            logger.warning(f"No verification session found for session ID: {session_id}")
            return None

        discord_id, expiry_time = session_data

        if datetime.now() > expiry_time:
            logger.warning(f"Verification session {session_id} has expired")
            del _verification_sessions[session_id]
            return None

        del _verification_sessions[session_id]

        current_time = datetime.now().isoformat()
        user_res = await supabase.table("users").select("*").eq("discord_id", discord_id).neq("verification_token", None).gt("verification_token_expires_at", current_time).limit(1).execute()

        if not user_res.data:
            logger.warning(f"No valid pending verification found for Discord ID: {discord_id}")
            return None

        user_to_verify = user_res.data[0]

        existing_github_user = await supabase.table("users").select("*").eq("github_id", github_id).neq("id", user_to_verify['id']).limit(1).execute()
        if existing_github_user.data:
            logger.warning(f"GitHub account {github_username} is already linked to another user")
            await supabase.table("users").update({
                "verification_token": None,
                "verification_token_expires_at": None,
                "updated_at": datetime.now().isoformat()
            }).eq("id", user_to_verify['id']).execute()
            raise Exception(f"GitHub account {github_username} is already linked to another Discord user")

        update_data = {
            "github_id": github_id,
            "github_username": github_username,
            "email": user_to_verify.get('email') or email,
            "is_verified": True,
            "verified_at": datetime.now().isoformat(),
            "verification_token": None,
            "verification_token_expires_at": None,
            "updated_at": datetime.now().isoformat()
        }

        await supabase.table("users").update(update_data).eq("id", user_to_verify['id']).execute()

        updated_user_res = await supabase.table("users").select("*").eq("id", user_to_verify['id']).limit(1).execute()

        if not updated_user_res.data:
            raise Exception(f"Failed to fetch updated user with ID: {user_to_verify['id']}")

        logger.info(f"Successfully verified user {user_to_verify['id']} and linked GitHub account {github_username}.")
        return User(**updated_user_res.data[0])
    except Exception as e:
        logger.error(f"Database error in find_user_by_session_and_verify: {e}", exc_info=True)
        raise

async def cleanup_expired_tokens():
    """
    Clean up expired verification tokens from database.
    """
    supabase = get_supabase_client()
    current_time = datetime.now().isoformat()

    try:
        cleanup_res = await supabase.table("users").update({
            "verification_token": None,
            "verification_token_expires_at": None,
            "updated_at": current_time
        }).lt("verification_token_expires_at", current_time).neq("verification_token", None).execute()

        if cleanup_res.data:
            logger.info(f"Cleaned up {len(cleanup_res.data)} expired verification tokens from database")
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")

async def get_verification_session_info(session_id: str) -> Optional[Dict[str, str]]:
    """
    Get information about a verification session.
    """
    _cleanup_expired_sessions()

    session_data = _verification_sessions.get(session_id)
    if not session_data:
        return None

    discord_id, expiry_time = session_data

    if datetime.now() > expiry_time:
        del _verification_sessions[session_id]
        return None

    return {
        "discord_id": discord_id,
        "expiry_time": expiry_time.isoformat(),
        "time_remaining": str(expiry_time - datetime.now())
    }
