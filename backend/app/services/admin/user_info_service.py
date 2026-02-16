import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.database.supabase.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:
    discord_id: str
    discord_username: str
    display_name: str
    avatar_url: Optional[str]
    created_at: str
    is_verified: bool
    github_username: Optional[str]
    message_count: int
    has_active_thread: bool
    roles_count: int
    last_message_at: Optional[str]


class UserInfoService:
    def __init__(self, bot=None):
        self.bot = bot

    async def _get_internal_user_id(self, discord_id: str) -> Optional[str]:
        """Resolve internal users.id UUID from a Discord snowflake ID."""
        try:
            supabase = get_supabase_client()
            res = await supabase.table("users").select("id").eq(
                "discord_id", discord_id
            ).limit(1).execute()

            if res.data:
                return str(res.data[0]["id"])
            return None
        except Exception as e:
            logger.warning(f"Could not resolve internal user id for discord_id={discord_id}: {e}")
            return None

    async def get_user_profile(self, discord_id: str) -> Optional[Dict[str, Any]]:
        try:
            supabase = get_supabase_client()
            res = await supabase.table("users").select("*").eq(
                "discord_id", discord_id
            ).limit(1).execute()
            if res.data:
                return res.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

    async def get_user_message_count(self, discord_id: str) -> int:
        try:
            internal_user_id = await self._get_internal_user_id(discord_id)
            if not internal_user_id:
                return 0

            supabase = get_supabase_client()
            res = await supabase.table("interactions").select(
                "id", count="exact"
            ).eq("user_id", internal_user_id).execute()
            return res.count or 0
        except Exception as e:
            logger.warning(f"Could not get message count: {e}")
            return 0

    async def get_last_message(self, discord_id: str) -> Optional[str]:
        try:
            internal_user_id = await self._get_internal_user_id(discord_id)
            if not internal_user_id:
                return None

            supabase = get_supabase_client()
            res = await supabase.table("interactions").select(
                "created_at"
            ).eq("user_id", internal_user_id).order(
                "created_at", desc=True
            ).limit(1).execute()
            if res.data:
                return res.data[0]["created_at"]
            return None
        except Exception as e:
            logger.warning(f"Could not get last message: {e}")
            return None

    def has_active_thread(self, discord_id: str) -> bool:
        if not self.bot:
            return False
        return discord_id in self.bot.active_threads

    async def get_full_user_info(
        self,
        discord_user,
        member=None
    ) -> UserInfo:
        discord_id = str(discord_user.id)
        profile = await self.get_user_profile(discord_id)
        message_count = await self.get_user_message_count(discord_id)
        last_message = await self.get_last_message(discord_id)

        is_verified = False
        github_username = None
        if profile:
            is_verified = profile.get("is_verified", False)
            github_username = profile.get("github_username")

        roles_count = len(member.roles) - 1 if member else 0

        return UserInfo(
            discord_id=discord_id,
            discord_username=discord_user.name,
            display_name=discord_user.display_name if hasattr(discord_user, 'display_name') else discord_user.name,
            avatar_url=str(discord_user.avatar.url) if discord_user.avatar else None,
            created_at=discord_user.created_at.strftime("%Y-%m-%d"),
            is_verified=is_verified,
            github_username=github_username,
            message_count=message_count,
            has_active_thread=self.has_active_thread(discord_id),
            roles_count=roles_count,
            last_message_at=last_message,
        )
