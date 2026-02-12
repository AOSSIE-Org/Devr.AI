from typing import Optional, Dict, Any
from app.database.supabase.client import get_supabase_client
import logging
import secrets
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

async def store_oauth_state(session_id: str, ttl: int = 300) -> str:
    """
    Generate and store a cryptographically secure OAuth state token in Redis.
    """
    try:
        state_token = secrets.token_urlsafe(32)
        redis_client = await get_redis_client()

        # Store: oauth_state:{state_token} -> session_id
        redis_key = f"oauth_state:{state_token}"
        await redis_client.setex(redis_key, ttl, session_id)

        logger.info(f"OAuth state stored for session: {session_id[:8]}... (expires in {ttl}s)")
        return state_token

    except Exception as e:
        logger.error(f"Failed to store OAuth state: {str(e)}", exc_info=True)
        raise Exception("OAuth state storage failed. Verification service temporarily unavailable.") from e

async def validate_oauth_state(state_token: str, expected_session_id: str) -> bool:
    """
    Validate and consume an OAuth state token.
    """
    try:
        redis_client = await get_redis_client()
        redis_key = f"oauth_state:{state_token}"

        # Atomic retrieval and deletion using Lua script
        lua_script = """
        local key = KEYS[1]
        local expected = ARGV[1]
        local stored = redis.call('GET', key)
        
        if stored == expected then
            redis.call('DEL', key)
            return 1
        else
            return 0
        end
        """

        result = await redis_client.eval(lua_script, 1, redis_key, expected_session_id)

        if result == 1:
            logger.info(f"OAuth state validated successfully for session: {expected_session_id[:8]}...")
            return True
        else:
            logger.warning("OAuth state validation failed - mismatch or missing state")
            return False

    except Exception as e:
        logger.error(f"OAuth state validation error: {str(e)}", exc_info=True)
        return False

async def login_with_oauth(provider: str, redirect_to: Optional[str] = None, state: Optional[str] = None):
    """
    Generates an asynchronous OAuth sign-in URL.
    """
    supabase = get_supabase_client()
    try:
        options: Dict[str, Any] = {}
        if redirect_to:
            options['redirect_to'] = redirect_to
        if state:
            options['queryParams'] = {'state': state}

        result = await supabase.auth.sign_in_with_oauth({
            "provider": provider,
            "options": options
        })
        return {"url": result.url}
    except Exception as e:
        logger.error(f"OAuth login failed for provider {provider}: {e}", exc_info=True)
        raise

async def login_with_github(redirect_to: Optional[str] = None, state: Optional[str] = None):
    """Generates a GitHub OAuth login URL."""
    return await login_with_oauth("github", redirect_to=redirect_to, state=state)

async def login_with_discord(redirect_to: Optional[str] = None):
    """Generates a Discord OAuth login URL."""
    return await login_with_oauth("discord", redirect_to=redirect_to)

async def login_with_slack(redirect_to: Optional[str] = None):
    """Generates a Slack OAuth login URL."""
    return await login_with_oauth("slack", redirect_to=redirect_to)

async def logout(access_token: str):
    """Logs out a user by revoking their session."""
    supabase = get_supabase_client()
    try:
        await supabase.auth.set_session(access_token, refresh_token="")  # nosec
        await supabase.auth.sign_out()
        return {"message": "User logged out successfully"}
    except Exception as e:
        logger.error(f"Logout failed: {e}", exc_info=True)
        raise
