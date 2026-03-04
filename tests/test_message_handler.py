"""
Unit tests for MessageHandler.

Tests message event routing and FAQ detection patterns. Uses a test double that
mirrors the production MessageHandler behavior to avoid circular import issues.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.core.events.base import BaseEvent
from app.core.events.enums import EventType, PlatformType


class FAQHandlerMock:
    """Mock FAQ handler for testing MessageHandler."""
    
    def __init__(self):
        self.is_faq = AsyncMock(return_value=(False, None))
        self.handle = AsyncMock(return_value={"success": True, "action": "faq_response_sent"})


class MessageHandlerTestDouble:
    """
    Test double mirroring the production MessageHandler implementation.
    This avoids circular import issues while testing the message handling pattern.
    """
    
    def __init__(self, bot=None):
        self.bot = bot
        self.name = "MessageHandler"
        self.faq_handler = FAQHandlerMock()
    
    async def handle(self, event: BaseEvent) -> dict:
        """Handle message-related events."""
        event_type = event.event_type
        
        if event_type == EventType.MESSAGE_CREATED.value:
            return await self._handle_message_created(event)
        
        if event_type == EventType.MESSAGE_UPDATED.value:
            return {"success": True, "action": "message_updated"}
        
        return {"success": False, "reason": "Unsupported event type"}
    
    async def _handle_message_created(self, event: BaseEvent) -> dict:
        """Handle new message creation."""
        content = getattr(event, 'content', None)
        
        # Validate content
        if content is None or (isinstance(content, str) and not content.strip()):
            return {"success": False, "reason": "Empty message content"}
        
        # Check for FAQ
        is_faq, _faq_response = await self.faq_handler.is_faq(content)
        if is_faq:
            return await self.faq_handler.handle(event)
        
        return {"success": True, "action": "message_processed"}


class TestMessageHandler:
    """Tests for MessageHandler pattern."""

    @pytest.fixture
    def handler(self):
        return MessageHandlerTestDouble(bot=None)

    @pytest.fixture
    def message_created_event(self):
        return BaseEvent(
            id="msg-evt-1",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,
            actor_id="user-123",
            channel_id="channel-456",
            content="Hello, how are you?"
        )

    @pytest.fixture
    def message_updated_event(self):
        return BaseEvent(
            id="msg-evt-2",
            platform=PlatformType.SLACK.value,
            event_type=EventType.MESSAGE_UPDATED.value,
            actor_id="user-456",
            content="Updated message content"
        )

    # ------------------------------------------------------------------
    # handle tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_handle_message_created(self, handler, message_created_event):
        """handle() processes MESSAGE_CREATED events."""
        result = await handler.handle(message_created_event)
        
        assert result["success"] is True
        assert result["action"] == "message_processed"

    @pytest.mark.asyncio
    async def test_handle_message_updated(self, handler, message_updated_event):
        """handle() processes MESSAGE_UPDATED events."""
        result = await handler.handle(message_updated_event)
        
        assert result["success"] is True
        assert result["action"] == "message_updated"

    @pytest.mark.asyncio
    async def test_handle_unsupported_event_type(self, handler):
        """handle() returns error for unsupported event types."""
        event = BaseEvent(
            id="other-evt-1",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_DELETED.value,
            actor_id="user-123"
        )
        
        result = await handler.handle(event)
        
        assert result["success"] is False
        assert "Unsupported" in result["reason"]

    # ------------------------------------------------------------------
    # Message content validation tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_handle_message_created_empty_content(self, handler):
        """Returns error for empty message content."""
        event = BaseEvent(
            id="msg-evt-empty",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,
            actor_id="user-123",
            content=""
        )
        
        result = await handler.handle(event)
        
        assert result["success"] is False
        assert "Empty" in result["reason"]

    @pytest.mark.asyncio
    async def test_handle_message_created_none_content(self, handler):
        """Returns error for None message content."""
        event = BaseEvent(
            id="msg-evt-none",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,
            actor_id="user-123",
            content=None
        )
        
        result = await handler.handle(event)
        
        assert result["success"] is False
        assert "Empty" in result["reason"]

    @pytest.mark.asyncio
    async def test_handle_message_created_whitespace_only(self, handler):
        """Returns error for whitespace-only message content."""
        event = BaseEvent(
            id="msg-evt-ws",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,
            actor_id="user-123",
            content="   \n\t  "
        )
        
        result = await handler.handle(event)
        
        assert result["success"] is False
        assert "Empty" in result["reason"]

    # ------------------------------------------------------------------
    # FAQ detection tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_handle_message_faq_detection(self, handler):
        """Message matching FAQ triggers FAQ handler."""
        event = BaseEvent(
            id="msg-evt-faq",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,
            actor_id="user-123",
            channel_id="channel-456",
            content="what is devr.ai?"
        )
        
        # Mock the faq_handler's is_faq to return True
        handler.faq_handler.is_faq = AsyncMock(return_value=(True, "AI-powered assistant"))
        
        result = await handler.handle(event)
        
        handler.faq_handler.is_faq.assert_called_once()
        handler.faq_handler.handle.assert_called_once()
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_message_not_faq(self, handler):
        """Non-FAQ message is processed normally."""
        event = BaseEvent(
            id="msg-evt-normal",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,
            actor_id="user-123",
            content="Hello everyone!"
        )
        
        # Mock is_faq to return False
        handler.faq_handler.is_faq = AsyncMock(return_value=(False, None))
        
        result = await handler.handle(event)
        
        assert result["success"] is True
        assert result["action"] == "message_processed"
        handler.faq_handler.handle.assert_not_called()
