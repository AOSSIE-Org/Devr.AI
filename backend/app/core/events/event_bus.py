from typing import Dict, List, Union, Optional
from .base import BaseEvent
from .enums import EventType, PlatformType

class EventBus:
    """Central event bus for dispatching events to registered handlers"""
    def __init__(self):
        self.handlers = {}
        self.global_handlers = []
    
    def register_handler(self, event_type: Union[EventType, List[EventType]], handler_func, platform: Optional[PlatformType] = None):
        """Register a handler function for a specific event type and optionally platform"""
        pass
    
    def register_global_handler(self, handler_func):
        """Register a handler that will receive all events"""
        pass

    async def dispatch(self, event: BaseEvent):
        """Dispatch an event to all registered handlers"""
        pass