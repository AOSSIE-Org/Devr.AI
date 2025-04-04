import asyncio
import logging
from typing import Dict, List, Union, Optional
from .base import BaseEvent
from .enums import EventType, PlatformType
from ..handler.handler_registry import HandlerRegistry

logger = logging.getLogger(__name__)

class EventBus:
    """
    Central event bus for dispatching events to registered handlers.
    
    The EventBus manages the registration of event handlers and dispatches
    incoming events to the appropriate registered handlers. It supports
    both event-specific handlers and global handlers that receive all events.
    
    Attributes:
        handler_registry (HandlerRegistry): Registry containing handler information
        handlers (Dict[EventType, List[callable]]): Dictionary mapping event types to handler functions
        global_handlers (List[callable]): List of handlers that receive all events
    """
    
    def __init__(self, handler_registry: HandlerRegistry):
        """
        Initialize the EventBus with a handler registry.
        
        Args:
            handler_registry (HandlerRegistry): Registry for managing handlers
        """
        self.handler_registry = handler_registry
        self.handlers: Dict[EventType, List[callable]] = {}
        self.global_handlers: List[callable] = []
    
    def register_handler(self, event_type: Union[EventType, List[EventType]], handler_func, platform: Optional[PlatformType] = None):
        """
        Register a handler function for one or more specific event types.
        
        Args:
            event_type (Union[EventType, List[EventType]]): Event type(s) to register the handler for
            handler_func (callable): Handler function to be called when the event occurs
            platform (Optional[PlatformType]): Platform to restrict the handler to (not implemented)
            
        Note:
            The platform parameter is not currently used in the implementation
        """
        # Handle both single event type and list of event types
        if isinstance(event_type, list):
            for et in event_type:
                self._add_handler(et, handler_func)
        else:
            self._add_handler(event_type, handler_func)
        
        logger.info(f"Handler {handler_func.__name__} registered for event type {event_type}")
    
    def _add_handler(self, event_type: EventType, handler_func: callable):
        """
        Internal method to add a handler to the handlers dictionary.
        
        Args:
            event_type (EventType): The event type to register for
            handler_func (callable): The handler function to register
        """
        # Initialize the list for this event type if it doesn't exist
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        # Add the handler to the list for this event type
        self.handlers[event_type].append(handler_func)
    
    def register_global_handler(self, handler_func):
        """
        Register a handler that will receive all events regardless of type.
        
        Args:
            handler_func (callable): Handler function to be called for all events
        """
        self.global_handlers.append(handler_func)
        logger.info(f"Global handler {handler_func.__name__} registered")
    
    async def dispatch(self, event: BaseEvent):
        """
        Dispatch an event to all registered handlers.
        
        This method will:
        1. Call all global handlers
        2. Call all handlers registered for the specific event type
        
        All handlers are called asynchronously using asyncio.create_task
        
        Args:
            event (BaseEvent): The event to dispatch
        """
        logger.info(f"Dispatching event {event.id} of type {event.event_type}")
        
        # Call global handlers first
        for handler in self.global_handlers:
            # Create an asyncio task to run the handler asynchronously
            asyncio.create_task(handler(event))
        
        # Call event-specific handlers
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                asyncio.create_task(handler(event))
        else:
            logger.info(f"No handlers registered for event type {event.event_type}")
