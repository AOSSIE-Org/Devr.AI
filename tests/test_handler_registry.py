"""
Unit tests for HandlerRegistry.

Tests registration and lookup of event handlers by event type and platform.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import pytest
from unittest.mock import MagicMock

# Import directly from specific modules to avoid circular import via __init__.py
from app.core.events.base import BaseEvent
from app.core.events.enums import EventType, PlatformType
from app.core.handler.base import BaseHandler


class MockHandler(BaseHandler):
    """Concrete handler for testing."""
    async def handle(self, event: BaseEvent):
        return {"handled": True, "handler": "MockHandler"}


class AnotherMockHandler(BaseHandler):
    """Another concrete handler for testing."""
    async def handle(self, event: BaseEvent):
        return {"handled": True, "handler": "AnotherMockHandler"}


class DiscordSpecificHandler(BaseHandler):
    """Platform-specific handler for Discord."""
    async def handle(self, event: BaseEvent):
        return {"handled": True, "handler": "DiscordSpecificHandler"}


# Lazy import to avoid circular dependency
def get_handler_registry():
    from app.core.handler.handler_registry import HandlerRegistry
    return HandlerRegistry()


class TestHandlerRegistry:
    """Tests for HandlerRegistry class."""

    @pytest.fixture
    def registry(self):
        return get_handler_registry()

    def test_register_single_event_type(self, registry):
        """Registering a handler for a single event type works."""
        registry.register([EventType.MESSAGE_CREATED], MockHandler)
        
        assert EventType.MESSAGE_CREATED.value in registry.handlers
        assert registry.handlers[EventType.MESSAGE_CREATED.value] == MockHandler

    def test_register_multiple_event_types(self, registry):
        """Registering a handler for multiple event types works."""
        event_types = [EventType.MESSAGE_CREATED, EventType.MESSAGE_UPDATED]
        registry.register(event_types, MockHandler)
        
        assert EventType.MESSAGE_CREATED.value in registry.handlers
        assert EventType.MESSAGE_UPDATED.value in registry.handlers

    def test_register_platform_specific_handler(self, registry):
        """Registering a platform-specific handler uses correct key format."""
        registry.register(
            [EventType.MESSAGE_CREATED], 
            DiscordSpecificHandler, 
            platform=PlatformType.DISCORD
        )
        
        expected_key = f"{PlatformType.DISCORD.value}:{EventType.MESSAGE_CREATED.value}"
        assert expected_key in registry.handlers
        assert registry.handlers[expected_key] == DiscordSpecificHandler

    def test_get_handler_platform_specific(self, registry):
        """Getting a handler for a platform-specific event returns the correct handler."""
        # Register platform-specific handler
        registry.register(
            [EventType.MESSAGE_CREATED], 
            DiscordSpecificHandler, 
            platform=PlatformType.DISCORD
        )
        # Register generic fallback
        registry.register([EventType.MESSAGE_CREATED], MockHandler)
        
        # Create event - pass enums so get_handler can call .value
        event = BaseEvent(
            id="test-1",
            platform=PlatformType.DISCORD,
            event_type=EventType.MESSAGE_CREATED,
            actor_id="user-1"
        )
        
        handler = registry.get_handler(event)
        assert isinstance(handler, DiscordSpecificHandler)

    def test_get_handler_fallback_to_generic(self, registry):
        """Falls back to generic handler when no platform-specific handler exists."""
        # Only register generic handler
        registry.register([EventType.MESSAGE_CREATED], MockHandler)
        
        event = BaseEvent(
            id="test-1",
            platform=PlatformType.SLACK,  # No Slack-specific handler registered
            event_type=EventType.MESSAGE_CREATED,
            actor_id="user-1"
        )
        
        handler = registry.get_handler(event)
        assert isinstance(handler, MockHandler)

    def test_get_handler_raises_for_unregistered_event(self, registry):
        """Raises ValueError when no handler is registered for the event type."""
        event = BaseEvent(
            id="test-1",
            platform=PlatformType.DISCORD,
            event_type=EventType.ISSUE_CREATED,  # Not registered
            actor_id="user-1"
        )
        
        with pytest.raises(ValueError) as exc_info:
            registry.get_handler(event)
        
        assert "No handler registered" in str(exc_info.value)

    def test_handler_instance_caching(self, registry):
        """Handler instances are cached and reused."""
        registry.register([EventType.MESSAGE_CREATED], MockHandler)
        
        event = BaseEvent(
            id="test-1",
            platform=PlatformType.DISCORD,
            event_type=EventType.MESSAGE_CREATED,
            actor_id="user-1"
        )
        
        handler1 = registry.get_handler(event)
        handler2 = registry.get_handler(event)
        
        # Same instance should be returned
        assert handler1 is handler2

    def test_different_event_types_different_handlers(self, registry):
        """Different event types can have different handlers."""
        registry.register([EventType.MESSAGE_CREATED], MockHandler)
        registry.register([EventType.ISSUE_CREATED], AnotherMockHandler)
        
        msg_event = BaseEvent(
            id="test-1",
            platform=PlatformType.DISCORD,
            event_type=EventType.MESSAGE_CREATED,
            actor_id="user-1"
        )
        issue_event = BaseEvent(
            id="test-2",
            platform=PlatformType.GITHUB,
            event_type=EventType.ISSUE_CREATED,
            actor_id="user-1"
        )
        
        msg_handler = registry.get_handler(msg_event)
        issue_handler = registry.get_handler(issue_event)
        
        assert isinstance(msg_handler, MockHandler)
        assert isinstance(issue_handler, AnotherMockHandler)
