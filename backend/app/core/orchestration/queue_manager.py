import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class QueuePriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AsyncQueueManager:
    """AsyncIO-based queue manager for agent orchestration"""

    def __init__(self):
        self.queues = {
            QueuePriority.HIGH: asyncio.Queue(),
            QueuePriority.MEDIUM: asyncio.Queue(),
            QueuePriority.LOW: asyncio.Queue()
        }
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.worker_tasks = []

    async def start(self, num_workers: int = 3):
        """Start the queue processing workers"""
        self.running = True

        for i in range(num_workers):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self.worker_tasks.append(task)

        logger.info(f"Started {num_workers} queue workers")

    async def stop(self):
        """Stop the queue processing"""
        self.running = False

        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()

        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        logger.info("Stopped all queue workers")

    async def enqueue(self,
                      message: Dict[str, Any],
                      priority: QueuePriority = QueuePriority.MEDIUM,
                      delay: float = 0):
        """Add a message to the queue"""

        if delay > 0:
            await asyncio.sleep(delay)

        queue_item = {
            "id": message.get("id", f"msg_{datetime.now().timestamp()}"),
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "data": message
        }

        await self.queues[priority].put(queue_item)
        logger.debug(f"Enqueued message {queue_item['id']} with priority {priority}")

    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def _worker(self, worker_name: str):
        """Worker coroutine to process queue items"""
        logger.info(f"Started queue worker: {worker_name}")

        while self.running:
            try:
                # Process queues by priority
                item = await self._get_next_item()

                if item:
                    await self._process_item(item, worker_name)
                else:
                    # No items available, wait a bit
                    await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Connection error in worker {worker_name}: {str(e)}")
                await asyncio.sleep(5)  # Longer pause for connection issues
            except Exception as e:
                logger.error(f"Unexpected error in worker {worker_name}: {str(e)}")
                await asyncio.sleep(1)  # Brief pause on error

    async def _get_next_item(self) -> Optional[Dict[str, Any]]:
        """Get the next item from queues (priority-based)"""

        # Try high priority first
        try:
            return self.queues[QueuePriority.HIGH].get_nowait()
        except asyncio.QueueEmpty:
            pass

        # Then medium priority
        try:
            return self.queues[QueuePriority.MEDIUM].get_nowait()
        except asyncio.QueueEmpty:
            pass

        # Finally low priority
        try:
            return self.queues[QueuePriority.LOW].get_nowait()
        except asyncio.QueueEmpty:
            pass

        return None

    async def _process_item(self, item: Dict[str, Any], worker_name: str):
        """Process a queue item"""
        try:
            message_data = item["data"]
            message_type = message_data.get("type", "unknown")

            handler = self.handlers.get(message_type)

            if handler:
                logger.debug(f"Worker {worker_name} processing {item['id']} (type: {message_type})")
                await handler(message_data)
            else:
                logger.warning(f"No handler found for message type: {message_type}")

        except Exception as e:
            logger.error(f"Error processing item {item['id']}: {str(e)}")
