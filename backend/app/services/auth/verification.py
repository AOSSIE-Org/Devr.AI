import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
from app.database.supabase.client import get_supabase_client
from app.models.database.supabase import User
import logging

logger = logging.getLogger(__name__)

# session_id -> (discord_id, expiry_time)
_verification_sessions: Dict[str, Tuple[str, datetime]] = {}

SESSION_EXPIRY_MINUTES = 5

def _cleanup_expired_sessions():
    """
    Remove expired verification sessions.
    """
    current_time = datetime.now(timezone.utc) 
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

    await cleanup_expired_tokens()
    _cleanup_expired_sessions()

    token = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=SESSION_EXPIRY_MINUTES)

    try:
        update_res = await supabase.table("users").update({
            "verification_token": token,
            "verification_token_expires_at": expiry_time.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat() 
        }).eq("discord_id", discord_id).execute()

        if update_res.data:
            _verification_sessions[session_id] = (discord_id, expiry_time)
            logger.info(
                f"Created verification session {session_id} for Discord user {discord_id}, expires at {expiry_time}")
            return session_id
        logger.error(f"Failed to set verification token for Discord ID: {discord_id}. User not found.")
        return None
    except Exception as e:
        logger.error(f"Error creating verification session for Discord ID {discord_id}: {str(e)}")
        return None

async def find_user_by_session_and_verify(
    session_id: str, github_id: str, github_username: str, email: Optional[str]
) -> Optional[User]:
    """
    Find and verify user using session ID with expiry validation.
    Links GitHub account to Discord user.
    """
    supabase = get_supabase_client()

    _cleanup_expired_sessions()

    try:
        session_data = _verification_sessions.get(session_id)
        if not session_data:
            logger.warning(f"No verification session found for session ID: {session_id}")
            return None

        discord_id, expiry_time = session_data

        current_time = datetime.now(timezone.utc).isoformat()
        user_res = await supabase.table("users").select("*").eq(
            "discord_id", discord_id
        ).neq(
            "verification_token", None
        ).gt(
            "verification_token_expires_at", current_time
        ).limit(1).execute()

        if not user_res.data:
            logger.warning(f"No valid pending verification found for Discord ID: {discord_id} (token may have expired)")
            del _verification_sessions[session_id]
            return None

        # Delete the session after successful validation
        del _verification_sessions[session_id]

        user_to_verify = user_res.data[0]

        existing_github_user = await supabase.table("users").select("*").eq(
            "github_id", github_id
        ).neq("id", user_to_verify['id']).limit(1).execute()
        if existing_github_user.data:
            logger.warning(f"GitHub account {github_username} is already linked to another user")
            await supabase.table("users").update({
                "verification_token": None,
                "verification_token_expires_at": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", user_to_verify['id']).execute()
            raise Exception(f"GitHub account {github_username} is already linked to another Discord user")

        update_data = {
            "github_id": github_id,
            "github_username": github_username,
            "email": user_to_verify.get('email') or email,
            "is_verified": True,
            "verified_at": datetime.now(timezone.utc).isoformat(),
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
    current_time = datetime.now(timezone.utc).isoformat()

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

    if datetime.now(timezone.utc) > expiry_time:
        del _verification_sessions[session_id]
        return None

    return {
        "discord_id": discord_id,
        "expiry_time": expiry_time.isoformat(),
        "time_remaining": str(expiry_time - datetime.now(timezone.utc)) 
    }
