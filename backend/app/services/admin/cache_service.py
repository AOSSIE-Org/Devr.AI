import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CacheInfo:
    name: str
    size: int
    cleared: bool


class CacheService:
    def __init__(self, bot=None):
        self.bot = bot

    async def get_cache_sizes(self) -> Dict[str, int]:
        sizes = {
            "active_threads": 0,
            "embeddings": 0,
            "memories": 0,
        }

        if self.bot:
            sizes["active_threads"] = len(self.bot.active_threads)

        return sizes

    async def clear_active_threads(self) -> int:
        if not self.bot:
            return 0

        count = len(self.bot.active_threads)
        self.bot.active_threads.clear()
        logger.info(f"Cleared {count} active threads from cache")
        return count

    async def clear_embeddings(self) -> int:
        logger.info("Embeddings cache clear requested (no-op for now)")
        return 0

    async def clear_memories(self) -> int:
        logger.info("Memories cache clear requested (no-op for now)")
        return 0

    async def clear_cache(self, cache_type: str = "all") -> Dict[str, int]:
        cleared = {}

        if cache_type in ("all", "active_threads"):
            cleared["active_threads"] = await self.clear_active_threads()

        if cache_type in ("all", "embeddings"):
            cleared["embeddings"] = await self.clear_embeddings()

        if cache_type in ("all", "memories"):
            cleared["memories"] = await self.clear_memories()

        return cleared
