import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from enum import Enum
import aio_pika
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueuePriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AsyncQueueManager:
    """Queue manager for agent orchestration"""

    def __init__(self):
        self.queues = {
            QueuePriority.HIGH: 'high_task_queue',
            QueuePriority.MEDIUM: 'medium_task_queue',
            QueuePriority.LOW: 'low_task_queue'
        }
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.worker_tasks = []
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.abc.AbstractChannel] = None



    async def connect(self):
        try:
            rabbitmq_url = getattr(settings, 'rabbitmq_url', 'amqp://guest:guest@localhost/')
            self.connection = await aio_pika.connect_robust(rabbitmq_url)
            self.channel = await self.connection.channel()
            # Declare queues
            for queue_name in self.queues.values():
                await self.channel.declare_queue(queue_name, durable=True)
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}", exc_info=True)
            raise

    async def start(self, num_workers: int = 3):
        """Start the queue processing workers"""
        await self.connect()
        self.running = True

        for i in range(num_workers):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self.worker_tasks.append(task)

        logger.info(f"Started {num_workers} async queue workers")

    async def stop(self):
        """Stop the queue processing"""
        self.running = False

        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()

        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        logger.info("Stopped all queue workers and closed connection")

    async def enqueue(self,
                      message: Dict[str, Any],
                      priority: QueuePriority = QueuePriority.MEDIUM,
                      delay: float = 0):
        """Add a message to the queue"""

        if delay > 0:
            await asyncio.sleep(delay)

        # Guard against publishing while disconnected
        if not self.channel or self.channel.is_closed:
            raise RuntimeError("Queue channel is not connected. Call start() before enqueue().")

        queue_item = {
            "id": message.get("id", f"msg_{datetime.now().timestamp()}"),
            "priority": priority.value,  # Serialize enum to string
            "data": message
        }
        json_message = json.dumps(queue_item).encode()
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json_message,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json"
            ),
            routing_key=self.queues[priority]
        )
        logger.info(f"Enqueued message {queue_item['id']} with priority {priority}")

    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def _worker(self, worker_name: str):
        """Worker coroutine to process queue items"""
        logger.info(f"Started queue worker: {worker_name}")
        # Each worker listens to all queues by priority
        queues = [
            await self.channel.declare_queue(self.queues[priority], durable=True)
            for priority in [QueuePriority.HIGH, QueuePriority.MEDIUM, QueuePriority.LOW]
        ]
        while self.running:
            for queue in queues:
                try:
                    message = await queue.get(no_ack=False, fail=False)
                    if message:
                        try:
                            item = json.loads(message.body.decode())
                            await self._process_item(item, worker_name)
                            await message.ack()
                        except Exception as e:
                            logger.error("Error processing message: %s", e, exc_info=True)
                            await message.nack(requeue=False)
                except asyncio.CancelledError:
                    logger.info(f"Worker {worker_name} cancelled")
                    return
                except Exception as e:
                    logger.error("Worker %s error: %s", worker_name, e, exc_info=True)
            await asyncio.sleep(0.1)

    async def _process_item(self, item: Dict[str, Any], worker_name: str):
        """Process a queue item"""
        try:
            message_data = item["data"]
            message_type = message_data.get("type", "unknown")

            handler = self.handlers.get(message_type)

            if handler:
                logger.debug(f"Worker {worker_name} processing {item['id']} (type: {message_type})")
                if asyncio.iscoroutinefunction(handler):
                    await handler(message_data)
                else:
                    handler(message_data)
            else:
                logger.warning(f"No handler found for message type: {message_type}")

        except Exception as e:
            logger.error(f"Error processing item {item.get('id', 'unknown')}: {str(e)}")
