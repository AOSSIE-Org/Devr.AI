import logging
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.database.supabase.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class BotStats:
    guild_count: int
    total_members: int
    active_threads: int
    latency_ms: int
    uptime_seconds: float
    memory_mb: float
    messages_today: int
    messages_week: int
    queue_high: int
    queue_medium: int
    queue_low: int


class BotStatsService:
    def __init__(self, bot=None, queue_manager=None):
        self.bot = bot
        self.queue_manager = queue_manager
        self._start_time = datetime.now()

    async def get_message_stats(self) -> Dict[str, int]:
        try:
            supabase = get_supabase_client()
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)

            today_res = await supabase.table("message_logs").select(
                "id", count="exact"
            ).gte("created_at", today_start.isoformat()).execute()

            week_res = await supabase.table("message_logs").select(
                "id", count="exact"
            ).gte("created_at", week_start.isoformat()).execute()

            return {
                "today": today_res.count or 0,
                "week": week_res.count or 0,
            }
        except Exception as e:
            logger.warning(f"Could not get message stats: {e}")
            return {"today": 0, "week": 0}

    async def get_queue_stats(self) -> Dict[str, int]:
        try:
            if not self.queue_manager or not self.queue_manager.channel:
                return {"high": 0, "medium": 0, "low": 0}

            stats = {}
            for priority, queue_name in self.queue_manager.queues.items():
                try:
                    queue = await self.queue_manager.channel.declare_queue(
                        queue_name, durable=True, passive=True
                    )
                    stats[priority.value] = queue.declaration_result.message_count
                except Exception:
                    stats[priority.value] = 0
            return stats
        except Exception as e:
            logger.warning(f"Could not get queue stats: {e}")
            return {"high": 0, "medium": 0, "low": 0}

    def get_system_stats(self) -> Dict[str, Any]:
        try:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            uptime = (datetime.now() - self._start_time).total_seconds()
            return {
                "memory_mb": round(memory_mb, 2),
                "uptime_seconds": uptime,
            }
        except Exception as e:
            logger.warning(f"Could not get system stats: {e}")
            return {"memory_mb": 0, "uptime_seconds": 0}

    async def get_all_stats(self) -> BotStats:
        message_stats = await self.get_message_stats()
        queue_stats = await self.get_queue_stats()
        system_stats = self.get_system_stats()

        guild_count = len(self.bot.guilds) if self.bot else 0
        total_members = sum(g.member_count or 0 for g in self.bot.guilds) if self.bot else 0
        active_threads = len(self.bot.active_threads) if self.bot else 0
        latency_ms = round(self.bot.latency * 1000) if self.bot else 0

        return BotStats(
            guild_count=guild_count,
            total_members=total_members,
            active_threads=active_threads,
            latency_ms=latency_ms,
            uptime_seconds=system_stats["uptime_seconds"],
            memory_mb=system_stats["memory_mb"],
            messages_today=message_stats["today"],
            messages_week=message_stats["week"],
            queue_high=queue_stats.get("high", 0),
            queue_medium=queue_stats.get("medium", 0),
            queue_low=queue_stats.get("low", 0),
        )
