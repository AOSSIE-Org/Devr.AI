import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from app.database.supabase.client import get_supabase_client
from app.models.database.supabase import User
import logging

logger = logging.getLogger(__name__)

# session_id -> (discord_id, expiry_time, oauth_state)
_verification_sessions: Dict[str, Tuple[str, datetime, str]] = {}

SESSION_EXPIRY_MINUTES = 5

def _cleanup_expired_sessions():
    """
    Remove expired verification sessions.
    """
    current_time = datetime.now()
    expired_sessions = [
        session_id for session_id, (discord_id, expiry_time, _state) in _verification_sessions.items()
        if current_time > expiry_time
    ]

    for session_id in expired_sessions:
        discord_id, _, _ = _verification_sessions[session_id]
        del _verification_sessions[session_id]
        logger.info(f"Cleaned up expired verification session {session_id} for Discord user {discord_id}")

    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired verification sessions")

async def create_verification_session(discord_id: str) -> Optional[Tuple[str, str]]:
    """
    Create a verification session with expiry and return (session_id, oauth_state).

    The OAuth ``state`` is a cryptographically-random token bound to the session.
    It must be threaded through the OAuth authorize URL and validated in the
    callback to protect against login CSRF (RFC 6749, Section 10.12).
    """
    supabase = get_supabase_client()

    _cleanup_expired_sessions()

    token = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    oauth_state = secrets.token_urlsafe(32)
    expiry_time = datetime.now() + timedelta(minutes=SESSION_EXPIRY_MINUTES)

    try:
        update_res = await supabase.table("users").update({
            "verification_token": token,
            "verification_token_expires_at": expiry_time.isoformat(),
            "updated_at": datetime.now().isoformat()
        }).eq("discord_id", discord_id).execute()

        if update_res.data:
            _verification_sessions[session_id] = (discord_id, expiry_time, oauth_state)
            logger.info(
                f"Created verification session {session_id} for Discord user {discord_id}, expires at {expiry_time}")
            return session_id, oauth_state
        logger.error(f"Failed to set verification token for Discord ID: {discord_id}. User not found.")
        return None
    except Exception as e:
        logger.error(f"Error creating verification session for Discord ID {discord_id}: {str(e)}")
        return None

def validate_oauth_state(session_id: str, state: Optional[str]) -> bool:
    """
    Validate the OAuth ``state`` returned in the callback against the value
    bound to the verification session.

    Uses a constant-time comparison and rejects missing/expired sessions or any
    mismatch. Does not consume the session (the session itself is consumed by
    :func:`find_user_by_session_and_verify`).
    """
    _cleanup_expired_sessions()

    if not state:
        logger.warning(f"OAuth state missing in callback for session ID: {session_id}")
        return False

    session_data = _verification_sessions.get(session_id)
    if not session_data:
        logger.warning(f"No verification session found while validating state for session ID: {session_id}")
        return False

    _discord_id, _expiry_time, expected_state = session_data

    if not secrets.compare_digest(state, expected_state):
        logger.warning(f"OAuth state mismatch for session ID: {session_id}")
        return False

    return True

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

        discord_id, _expiry_time, _oauth_state = session_data

        current_time = datetime.now().isoformat()
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

    discord_id, expiry_time, _oauth_state = session_data

    if datetime.now() > expiry_time:
        del _verification_sessions[session_id]
        return None

    return {
        "discord_id": discord_id,
        "expiry_time": expiry_time.isoformat(),
        "time_remaining": str(expiry_time - datetime.now())
    }
