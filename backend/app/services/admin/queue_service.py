import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from app.core.orchestration.queue_manager import QueuePriority

logger = logging.getLogger(__name__)


@dataclass
class QueueStats:
    priority: str
    pending: int
    consumers: int


@dataclass
class FullQueueStatus:
    high: QueueStats
    medium: QueueStats
    low: QueueStats
    total_pending: int


class QueueService:
    def __init__(self, queue_manager=None):
        self.queue_manager = queue_manager

    async def get_queue_stats(self) -> FullQueueStatus:
        high = QueueStats("high", 0, 0)
        medium = QueueStats("medium", 0, 0)
        low = QueueStats("low", 0, 0)

        if not self.queue_manager or not self.queue_manager.channel:
            return FullQueueStatus(high, medium, low, 0)

        try:
            for priority, queue_name in self.queue_manager.queues.items():
                try:
                    queue = await self.queue_manager.channel.declare_queue(
                        queue_name, durable=True, passive=True
                    )
                    count = queue.declaration_result.message_count
                    consumers = queue.declaration_result.consumer_count

                    if priority == QueuePriority.HIGH:
                        high = QueueStats("high", count, consumers)
                    elif priority == QueuePriority.MEDIUM:
                        medium = QueueStats("medium", count, consumers)
                    elif priority == QueuePriority.LOW:
                        low = QueueStats("low", count, consumers)
                except Exception as e:
                    logger.warning(f"Could not get stats for {queue_name}: {e}")

            total = high.pending + medium.pending + low.pending
            return FullQueueStatus(high, medium, low, total)
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return FullQueueStatus(high, medium, low, 0)

    async def clear_queue(self, priority: str = "all") -> Dict[str, int]:
        if not self.queue_manager or not self.queue_manager.channel:
            raise RuntimeError("Queue manager not available")

        cleared = {}

        try:
            priorities_to_clear = []
            if priority == "all":
                priorities_to_clear = list(self.queue_manager.queues.keys())
            else:
                priority_map = {
                    "high": QueuePriority.HIGH,
                    "medium": QueuePriority.MEDIUM,
                    "low": QueuePriority.LOW,
                }
                if priority in priority_map:
                    priorities_to_clear = [priority_map[priority]]

            for p in priorities_to_clear:
                queue_name = self.queue_manager.queues[p]
                try:
                    queue = await self.queue_manager.channel.declare_queue(
                        queue_name, durable=True, passive=True
                    )
                    count = queue.declaration_result.message_count
                    await queue.purge()
                    cleared[p.value] = count
                    logger.info(f"Cleared {count} messages from {queue_name}")
                except Exception as e:
                    logger.error(f"Failed to clear {queue_name}: {e}")
                    cleared[p.value] = 0

            return cleared
        except Exception as e:
            logger.error(f"Error clearing queues: {e}")
            raise
