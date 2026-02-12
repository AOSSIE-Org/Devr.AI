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
            logger.info(f"Registered handler '{handler_func.__name__}' for event types: {[et.value for et in event_type]}")
        else:
            self._add_handler(event_type, handler_func)
            logger.info(f"Registered handler '{handler_func.__name__}' for event type: {event_type.value}")
        
        if platform:
            logger.debug(f"Handler registered with platform filter: {platform.value}")

    def _add_handler(self, event_type: EventType, handler_func: callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
            logger.debug(f"Created new handler list for event type: {event_type.value}")

        # Check for duplicate handler registration
        if handler_func in self.handlers[event_type]:
            logger.warning(f"Handler '{handler_func.__name__}' already registered for {event_type.value}. Skipping duplicate.")
            return
        
        self.handlers[event_type].append(handler_func)
        logger.debug(f"Added handler '{handler_func.__name__}' to {event_type.value} (total: {len(self.handlers[event_type])})")

    def register_global_handler(self, handler_func):
        """Register a handler that will receive all events"""
        # Check for duplicate global handler registration
        if handler_func in self.global_handlers:
            logger.warning(f"Global handler '{handler_func.__name__}' already registered. Skipping duplicate.")
            return
        
        self.global_handlers.append(handler_func)
        logger.info(f"Registered global handler: {handler_func.__name__} (total global handlers: {len(self.global_handlers)})")

    async def dispatch(self, event: BaseEvent):
        """Dispatch an event to all registered handlers"""

        # Call global handlers first
        for handler in self.global_handlers:
            logger.info(f"Calling global handler: {handler.__name__}")
            asyncio.create_task(handler(event))

        # Call event-specific handlers
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                logger.info(f"Calling handler: {handler.__name__} for event type: {event.event_type}")
                asyncio.create_task(handler(event))
        else:
            logger.debug(f"No handlers registered for event type {event.event_type}")
