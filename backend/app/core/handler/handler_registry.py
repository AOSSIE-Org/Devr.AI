from typing import Dict, Type, List, Optional
from ..events.base import BaseEvent
from ..events.enums import EventType, PlatformType
from .base import BaseHandler

class HandlerRegistry:
    """Registry for event handlers"""
    
    def __init__(self):
        self.handlers: Dict[str, Type[BaseHandler]] = {}
        self.instances: Dict[str, BaseHandler] = {}
    
    def register(self, event_types: List[EventType], handler_class: Type[BaseHandler], 
                platform: Optional[PlatformType] = None):
        """Register a handler class for specific event types"""
        for event_type in event_types:
            key = f"{platform.value}:{event_type.value}" if platform else event_type.value
            self.handlers[key] = handler_class
    
    def get_handler(self, event: BaseEvent) -> BaseHandler:
        """Get handler instance for an event"""
        # Handle both enum and string values for platform and event_type
        platform_val = event.platform.value if hasattr(event.platform, 'value') else event.platform
        event_type_val = event.event_type.value if hasattr(event.event_type, 'value') else event.event_type
        
        # Try platform-specific handler first
        key = f"{platform_val}:{event_type_val}"
        handler_class = self.handlers.get(key)
        
        # Fall back to generic event type handler
        if not handler_class:
            key = event_type_val
            handler_class = self.handlers.get(key)
        
        if not handler_class:
            raise ValueError(f"No handler registered for event type {event.event_type} on platform {event.platform}")
        
        # Create instance if not cached
        if key not in self.instances:
            self.instances[key] = handler_class()
        
        return self.instances[key]