import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

from app.database.supabase.client import get_supabase_client
from app.core.orchestration.queue_manager import AsyncQueueManager, QueuePriority

logger = logging.getLogger(__name__)


@dataclass
class ResetResult:
    user_id: str
    memory_cleared: bool
    thread_closed: bool
    verification_reset: bool
    errors: List[str]


class UserManagementService:
    def __init__(self, bot=None, queue_manager: AsyncQueueManager = None):
        self.bot = bot
        self.queue_manager = queue_manager

    async def clear_user_memory(self, user_id: str) -> bool:
        try:
            if not self.queue_manager:
                logger.warning("Queue manager not available for memory clear")
                return False

            cleanup_msg = {
                "type": "clear_thread_memory",
                "memory_thread_id": user_id,
                "user_id": user_id,
                "cleanup_reason": "admin_reset"
            }
            await self.queue_manager.enqueue(cleanup_msg, QueuePriority.HIGH)
            logger.info(f"Queued memory clear for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory for {user_id}: {e}")
            return False

    async def close_user_thread(self, user_id: str) -> bool:
        try:
            if not self.bot:
                return False

            if user_id not in self.bot.active_threads:
                return True

            thread_id = self.bot.active_threads.pop(user_id, None)
            if thread_id:
                try:
                    thread = self.bot.get_channel(int(thread_id))
                    if thread:
                        await thread.edit(archived=True)
                        logger.info(f"Archived thread {thread_id} for user {user_id}")
                except Exception as e:
                    logger.warning(f"Could not archive thread {thread_id}: {e}")

            return True
        except Exception as e:
            logger.error(f"Failed to close thread for {user_id}: {e}")
            return False

    async def reset_verification(self, user_id: str) -> bool:
        try:
            supabase = get_supabase_client()
            await supabase.table("users").update({
                "github_id": None,
                "github_username": None,
                "is_verified": False,
                "verification_token": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("discord_id", user_id).execute()
            logger.info(f"Reset verification for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset verification for {user_id}: {e}")
            return False

    async def reset_user(
        self,
        user_id: str,
        reset_memory: bool = False,
        reset_thread: bool = False,
        reset_verification: bool = False
    ) -> ResetResult:
        errors = []
        memory_cleared = False
        thread_closed = False
        verification_reset = False

        if reset_memory:
            memory_cleared = await self.clear_user_memory(user_id)
            if not memory_cleared:
                errors.append("Failed to clear memory")

        if reset_thread:
            thread_closed = await self.close_user_thread(user_id)
            if not thread_closed:
                errors.append("Failed to close thread")

        if reset_verification:
            verification_reset = await self.reset_verification(user_id)
            if not verification_reset:
                errors.append("Failed to reset verification")

        return ResetResult(
            user_id=user_id,
            memory_cleared=memory_cleared,
            thread_closed=thread_closed,
            verification_reset=verification_reset,
            errors=errors
        )
