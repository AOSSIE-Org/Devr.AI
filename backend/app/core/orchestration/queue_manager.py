import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from enum import Enum
import aio_pika
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

# Single queue name for all priorities (broker handles ordering via x-max-priority)
DEFAULT_QUEUE_NAME = "task_queue"
MAX_PRIORITY = 10  # RabbitMQ priority 0-255; higher = more urgent


class QueuePriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Map enum to numeric priority for RabbitMQ (higher number = higher priority)
PRIORITY_MAP = {
    QueuePriority.HIGH: 10,
    QueuePriority.MEDIUM: 5,
    QueuePriority.LOW: 1,
}

class AsyncQueueManager:
    """Queue manager for agent orchestration using a single RabbitMQ priority queue."""

    def __init__(self, queue_name: str = DEFAULT_QUEUE_NAME):
        self.queue_name = queue_name
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.worker_tasks: list[asyncio.Task] = []
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.abc.AbstractChannel] = None

    async def connect(self) -> None:
        try:
            rabbitmq_url = getattr(
                settings, "rabbitmq_url", "amqp://guest:guest@localhost/"
            )
            self.connection = await aio_pika.connect_robust(rabbitmq_url)
            self.channel = await self.connection.channel()
            # Prefetch: broker sends at most this many unacked messages per consumer
            await self.channel.set_qos(prefetch_count=1)
            # Single priority queue: broker orders by message priority, no polling
            await self.channel.declare_queue(
                self.queue_name,
                durable=True,
                arguments={"x-max-priority": MAX_PRIORITY},
            )
            logger.info("Successfully connected to RabbitMQ (single priority queue)")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def start(self, num_workers: int = 3) -> None:
        """Start the queue processing workers (push-based consumers, no polling)."""
        await self.connect()
        self.running = True

        for i in range(num_workers):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self.worker_tasks.append(task)

        logger.info(f"Started {num_workers} async queue workers on {self.queue_name}")

    async def stop(self) -> None:
        """Stop the queue processing and close connections."""
        self.running = False

        for task in self.worker_tasks:
            task.cancel()

        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("Stopped all queue workers and closed connection")

    async def enqueue(
        self,
        message: Dict[str, Any],
        priority: QueuePriority = QueuePriority.MEDIUM,
        delay: float = 0,
    ) -> None:
        """Add a message to the single priority queue."""
        if delay > 0:
            await asyncio.sleep(delay)

        queue_item = {
            "id": message.get("id", f"msg_{datetime.now().timestamp()}"),
            "priority": priority.value,
            "data": message,
        }
        json_body = json.dumps(queue_item).encode()
        numeric_priority = PRIORITY_MAP[priority]

        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json_body, priority=numeric_priority),
            routing_key=self.queue_name,
        )
        logger.info(f"Enqueued message {queue_item['id']} with priority {priority}")

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a specific message type."""
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def _worker(self, worker_name: str) -> None:
        """Worker: long-lived consumer on the single queue (push-based, no polling)."""
        logger.info(f"Started queue worker: {worker_name}")

        queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,
            arguments={"x-max-priority": MAX_PRIORITY},
        )

        try:
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if not self.running:
                        break
                    try:
                        item = json.loads(message.body.decode())
                        await self._process_item(item, worker_name)
                        await message.ack()
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        await message.nack(requeue=False)
        except asyncio.CancelledError:
            logger.info(f"Worker {worker_name} cancelled")
        except Exception as e:
            logger.error(f"Worker {worker_name} error: {e}")

    async def _process_item(self, item: Dict[str, Any], worker_name: str) -> None:
        """Process a queue item by message type."""
        try:
            message_data = item["data"]
            message_type = message_data.get("type", "unknown")

            handler = self.handlers.get(message_type)

            if handler:
                logger.debug(
                    f"Worker {worker_name} processing {item['id']} (type: {message_type})"
                )
                if asyncio.iscoroutinefunction(handler):
                    await handler(message_data)
                else:
                    handler(message_data)
            else:
                logger.warning(f"No handler found for message type: {message_type}")

        except Exception as e:
            logger.error(f"Error processing item {item.get('id', 'unknown')}: {str(e)}")
