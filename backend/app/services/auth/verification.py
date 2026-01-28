import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.database.supabase.client import get_supabase_client
from app.models.database.supabase import User
from app.core.redis import get_redis_client
import logging

logger = logging.getLogger(__name__)

SESSION_EXPIRY_SECONDS = 300  # 5 minutes

class VerificationSessionStore:
    """
    Redis-backed store for verification sessions.
    Handles serialization of session data including datetimes.
    """
    PREFIX = "devr:auth:verification:"

    def __init__(self):
        self.redis = get_redis_client()

    def _get_key(self, session_id: str) -> str:
        return f"{self.PREFIX}{session_id}"

    async def save(self, session_id: str, discord_id: str, expiry_time: datetime):
        """Save session to Redis with TTL."""
        key = self._get_key(session_id)
        data = {
            "discord_id": discord_id,
            "expiry_time": expiry_time.isoformat()
        }
        # Redis expects seconds for ex
        await self.redis.set(
            key,
            json.dumps(data),
            ex=SESSION_EXPIRY_SECONDS
        )

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from Redis."""
        key = self._get_key(session_id)
        data_str = await self.redis.get(key)

        if not data_str:
            return None

        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode session data for {session_id}")
            return None

    async def delete(self, session_id: str):
        """Delete session from Redis."""
        key = self._get_key(session_id)
        await self.redis.delete(key)


async def create_verification_session(discord_id: str) -> Optional[str]:
    """
    Create a verification session with expiry and return session ID.
    """
    supabase = get_supabase_client()
    store = VerificationSessionStore()

    token = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    expiry_time = datetime.now() + timedelta(seconds=SESSION_EXPIRY_SECONDS)

    try:
        update_res = await supabase.table("users").update({
            "verification_token": token,
            "verification_token_expires_at": expiry_time.isoformat(),
            "updated_at": datetime.now().isoformat()
        }).eq("discord_id", discord_id).execute()

        if update_res.data:
            await store.save(session_id, discord_id, expiry_time)
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
    store = VerificationSessionStore()

    try:
        session_data = await store.get(session_id)
        if not session_data:
            logger.warning(f"No verification session found for session ID: {session_id}")
            return None

        discord_id = session_data["discord_id"]
        # We rely on Redis TTL for expiry, but can double check if needed
        # expiry_time = datetime.fromisoformat(session_data["expiry_time"])

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
            # Clean up Redis just in case
            await store.delete(session_id)
            return None

        # Atomic consumption: Delete the session immediately to prevent replay
        await store.delete(session_id)

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
    Note: Redis sessions expire automatically via TTL.
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
    store = VerificationSessionStore()

    session_data = await store.get(session_id)
    if not session_data:
        return None

    discord_id = session_data["discord_id"]
    expiry_time_str = session_data["expiry_time"]
    expiry_time = datetime.fromisoformat(expiry_time_str)

    # Calculate remaining time
    now = datetime.now()
    if now > expiry_time:
        await store.delete(session_id)
        return None

    return {
        "discord_id": discord_id,
        "expiry_time": expiry_time_str,
        "time_remaining": str(expiry_time - now)
    }
