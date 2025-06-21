from typing import Optional
from app.db.supabase.supabase_client import get_supabase_client
import logging

logger = logging.getLogger(__name__)

async def login_with_oauth(provider: str, redirect_to: Optional[str] = None, state: Optional[str] = None):
    """
    Generates an asynchronous OAuth sign-in URL.
    """
    supabase = get_supabase_client()
    try:
        options = {}
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
        await supabase.auth.set_session(access_token, refresh_token="")
        await supabase.auth.sign_out()
        return {"message": "User logged out successfully"}
    except Exception as e:
        logger.error(f"Logout failed: {e}", exc_info=True)
        raise
