import asyncio
import logging
from typing import Dict, List, Union, Optional
from .base import BaseEvent
from .enums import EventType, PlatformType
from ..handler.handler_registry import HandlerRegistry

logger = logging.getLogger(__name__)

class EventBus:
    """Central event bus for dispatching events to registered handlers"""

    def __init__(self, handler_registry: HandlerRegistry):
        self.handler_registry = handler_registry
        self.handlers: Dict[EventType, List[callable]] = {}
        self.global_handlers: List[callable] = []
        self._background_tasks: set[asyncio.Task] = set()

    def register_handler(self, event_type: Union[EventType, List[EventType]], handler_func, platform: Optional[PlatformType] = None):
        """Register a handler function for a specific event type and optionally platform"""
        if isinstance(event_type, list):
            for et in event_type:
                self._add_handler(et, handler_func)
        else:
            self._add_handler(event_type, handler_func)
        pass

    def _add_handler(self, event_type: EventType, handler_func: callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler_func)
        pass

    def register_global_handler(self, handler_func):
        """Register a handler that will receive all events"""
        self.global_handlers.append(handler_func)
        pass

    async def dispatch(self, event: BaseEvent):
        """Dispatch an event to all registered handlers"""

        async def _safe_call(handler, event):
            """Wrapper to catch and log exceptions from fire-and-forget handler tasks."""
            try:
                await handler(event)
            except Exception:
                logger.error(
                    "Event handler '%s' failed for event %s (type: %s)",
                    handler.__name__, event.id, event.event_type,
                    exc_info=True,
                )

        # Call global handlers first
        for handler in self.global_handlers:
            logger.info(f"Calling global handler: {handler.__name__}")
            task = asyncio.create_task(_safe_call(handler, event))
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        # Call event-specific handlers
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                logger.info(f"Calling handler: {handler.__name__} for event type: {event.event_type}")
                task = asyncio.create_task(_safe_call(handler, event))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
        else:
            logger.info(f"No handlers registered for event type {event.event_type}")
            pass
