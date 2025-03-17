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

    def register_handler(self, event_type: Union[EventType, List[EventType]], handler_func, platform: Optional[PlatformType] = None):
        """Register a handler function for a specific event type and optionally platform"""
        if isinstance(event_type, list):
            for et in event_type:
                self._add_handler(et, handler_func)
        else:
            self._add_handler(event_type, handler_func)
        logger.info(f"Handler {handler_func.__name__} registered for event type {event_type}")
        pass

    def _add_handler(self, event_type: EventType, handler_func: callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler_func)
        pass

    def register_global_handler(self, handler_func):
        """Register a handler that will receive all events"""
        self.global_handlers.append(handler_func)
        logger.info(f"Global handler {handler_func._name_} registered")
        pass

    async def dispatch(self, event: BaseEvent):
        """Dispatch an event to all registered handlers"""
        logger.info(f"Dispatching event {event.id} of type {event.event_type}")

        # Call global handlers first
        for handler in self.global_handlers:
            asyncio.create_task(handler(event))

        # Call event-specific handlers
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                asyncio.create_task(handler(event))

        else:
            logger.info(f"No handlers registered for event type {event.event_type}")
            pass
