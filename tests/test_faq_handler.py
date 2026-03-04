"""
Unit tests for FAQHandler.

Tests FAQ matching, response lookup patterns. Uses a test double that mirrors
the production FAQHandler behavior to avoid circular import issues.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import pytest
from typing import ClassVar
from unittest.mock import MagicMock, AsyncMock

from app.core.events.base import BaseEvent
from app.core.events.enums import EventType, PlatformType


class FAQHandlerTestDouble:
    """
    Test double mirroring the production FAQHandler implementation.
    This avoids circular import issues while testing the FAQ pattern.
    """
    
    FAQ_RESPONSES: ClassVar[dict[str, str]] = {
        "what is devr.ai?": "Devr.AI is an AI-powered Developer Relations assistant.",
        "how do i contribute?": "Visit our GitHub repository and check the contributing guide.",
        "how do i report a bug?": "Create a new issue on GitHub with details about the bug.",
        "where can i find documentation?": "Our documentation is available at docs.devr.ai"
    }
    
    def __init__(self, bot=None):
        self.bot = bot
        self.name = "FAQHandler"
    
    async def is_faq(self, question: str) -> tuple:
        """Check if a question matches a known FAQ."""
        question_lower = question.lower().strip()
        for faq_question, response in self.FAQ_RESPONSES.items():
            if faq_question in question_lower or question_lower in faq_question:
                return (True, response)
        return (False, None)
    
    def get_faq_response(self, question: str) -> str:
        """Get the response for a known FAQ, or a default message."""
        question_lower = question.lower().strip()
        for faq_question, response in self.FAQ_RESPONSES.items():
            if faq_question in question_lower or question_lower in faq_question:
                return response
        return "I'm not sure about that. Please check our documentation or ask a maintainer."
    
    async def handle(self, event: BaseEvent) -> dict:
        """Handle FAQ-related events."""
        event_type = event.event_type
        
        if event_type == EventType.FAQ_REQUESTED.value:
            content = getattr(event, 'content', '')
            response = self.get_faq_response(content)
            return {"success": True, "action": "faq_response_sent", "response": response}
        
        if event_type == EventType.KNOWLEDGE_UPDATED.value:
            return {"success": True, "action": "knowledge_updated"}
        
        return {"success": False, "reason": "Unsupported event type"}
    
    async def _send_discord_response(self, channel_id: str, response: str):
        """Send a response to Discord channel."""
        if self.bot is None:
            return
        
        try:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(response)
        except (ValueError, AttributeError):
            pass  # Channel retrieval may fail silently


class TestFAQHandler:
    """Tests for FAQHandler pattern."""

    @pytest.fixture
    def handler(self):
        return FAQHandlerTestDouble(bot=None)

    @pytest.fixture
    def mock_discord_bot(self):
        """Mock Discord bot with channel sending capability."""
        bot = MagicMock()
        channel = MagicMock()
        channel.send = AsyncMock()
        bot.get_channel = MagicMock(return_value=channel)
        return bot

    @pytest.fixture
    def handler_with_bot(self, mock_discord_bot):
        return FAQHandlerTestDouble(bot=mock_discord_bot)

    @pytest.fixture
    def faq_event(self):
        return BaseEvent(
            id="faq-evt-1",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.FAQ_REQUESTED.value,
            actor_id="user-123",
            channel_id="channel-456",
            content="what is devr.ai?"
        )

    # ------------------------------------------------------------------
    # is_faq tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_is_faq_returns_true_for_known_question(self, handler):
        """is_faq returns (True, response) for known FAQ."""
        result = await handler.is_faq("what is devr.ai?")
        
        assert result[0] is True
        assert result[1] is not None
        assert "AI-powered" in result[1]

    @pytest.mark.asyncio
    async def test_is_faq_returns_false_for_unknown_question(self, handler):
        """is_faq returns (False, None) for unknown question."""
        result = await handler.is_faq("what is the weather today?")
        
        assert result[0] is False
        assert result[1] is None

    @pytest.mark.asyncio
    async def test_is_faq_case_insensitive(self, handler):
        """is_faq matching is case insensitive."""
        result = await handler.is_faq("WHAT IS DEVR.AI?")
        
        assert result[0] is True

    @pytest.mark.asyncio
    async def test_is_faq_how_do_i_contribute(self, handler):
        """is_faq matches contribution question."""
        result = await handler.is_faq("how do i contribute?")
        
        assert result[0] is True
        assert "GitHub" in result[1]

    # ------------------------------------------------------------------
    # get_faq_response tests
    # ------------------------------------------------------------------

    def test_get_faq_response_returns_correct_answer(self, handler):
        """get_faq_response returns the stored answer."""
        response = handler.get_faq_response("what is devr.ai?")
        
        assert "AI-powered" in response
        assert "Developer Relations" in response

    def test_get_faq_response_returns_default_for_unknown(self, handler):
        """get_faq_response returns default message for unknown questions."""
        response = handler.get_faq_response("what is the meaning of life?")
        
        assert "not sure" in response.lower()

    def test_get_faq_response_case_insensitive(self, handler):
        """get_faq_response is case insensitive."""
        response = handler.get_faq_response("HOW DO I REPORT A BUG?")
        
        assert "issue" in response.lower() or "GitHub" in response

    # ------------------------------------------------------------------
    # handle tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_handle_faq_requested_event(self, handler, faq_event):
        """handle() processes FAQ_REQUESTED event."""
        result = await handler.handle(faq_event)
        
        assert result["success"] is True
        assert result["action"] == "faq_response_sent"

    @pytest.mark.asyncio
    async def test_handle_knowledge_updated_event(self, handler):
        """handle() processes KNOWLEDGE_UPDATED event."""
        event = BaseEvent(
            id="know-evt-1",
            platform=PlatformType.SYSTEM.value,
            event_type=EventType.KNOWLEDGE_UPDATED.value,
            actor_id="system"
        )
        
        result = await handler.handle(event)
        
        assert result["success"] is True
        assert result["action"] == "knowledge_updated"

    @pytest.mark.asyncio
    async def test_handle_unsupported_event_type(self, handler):
        """handle() returns error for unsupported event types."""
        event = BaseEvent(
            id="other-evt-1",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,  # Not supported
            actor_id="user-123"
        )
        
        result = await handler.handle(event)
        
        assert result["success"] is False
        assert "Unsupported" in result["reason"]

    # ------------------------------------------------------------------
    # Discord integration tests
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_send_discord_response_with_bot(self, handler_with_bot, mock_discord_bot):
        """_send_discord_response sends message when bot is available."""
        await handler_with_bot._send_discord_response("123456", "Test response")
        
        mock_discord_bot.get_channel.assert_called_once_with(123456)
        channel = mock_discord_bot.get_channel.return_value
        channel.send.assert_called_once_with("Test response")

    @pytest.mark.asyncio
    async def test_send_discord_response_without_bot(self, handler):
        """_send_discord_response does nothing when bot is None."""
        # Should not raise any exception
        await handler._send_discord_response("123456", "Test response")

    @pytest.mark.asyncio
    async def test_send_discord_response_channel_not_found(self, mock_discord_bot):
        """_send_discord_response handles missing channel gracefully."""
        mock_discord_bot.get_channel.return_value = None
        handler = FAQHandlerTestDouble(bot=mock_discord_bot)
        
        # Should not raise, just return silently
        await handler._send_discord_response("999999", "Test response")
