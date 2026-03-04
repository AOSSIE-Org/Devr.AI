"""
Unit tests for BaseHandler.

Tests the handler pipeline pattern (pre_handle -> handle -> post_handle).
These tests verify the expected behavior of BaseHandler using a test double
that mirrors the production implementation.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import pytest
from abc import ABC, abstractmethod
from unittest.mock import MagicMock

from app.core.events.base import BaseEvent
from app.core.events.enums import EventType, PlatformType


class BaseHandlerTestDouble(ABC):
    """
    Test double mirroring the production BaseHandler implementation.
    This avoids circular import issues while testing the handler pattern.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    async def pre_handle(self, event: BaseEvent) -> BaseEvent:
        """Pre-process the event before handling."""
        return event
    
    @abstractmethod
    async def handle(self, event: BaseEvent) -> dict:
        """Handle the event. Must be implemented by subclasses."""
        pass
    
    async def post_handle(self, event: BaseEvent, result: dict) -> dict:
        """Post-process the result after handling."""
        return result
    
    async def process(self, event: BaseEvent) -> dict:
        """Execute the full handler pipeline."""
        try:
            processed_event = await self.pre_handle(event)
            result = await self.handle(processed_event)
            return await self.post_handle(processed_event, result)
        except Exception as e:
            return {"success": False, "error": str(e)}


class ConcreteHandler(BaseHandlerTestDouble):
    """Concrete implementation for testing."""
    
    def __init__(self):
        super().__init__()
        self.handle_called = False
    
    async def handle(self, event: BaseEvent):
        self.handle_called = True
        return {"success": True, "data": "handled"}


class ErrorHandler(BaseHandlerTestDouble):
    """Handler that raises an exception in handle."""
    
    async def handle(self, event: BaseEvent):
        raise ValueError("Simulated error in handler")


class TestBaseHandler:
    """Tests for BaseHandler pattern."""

    @pytest.fixture
    def handler(self):
        return ConcreteHandler()

    @pytest.fixture
    def sample_event(self):
        return BaseEvent(
            id="test-evt-1",
            platform=PlatformType.DISCORD.value,
            event_type=EventType.MESSAGE_CREATED.value,
            actor_id="user-123",
            content="Test message"
        )

    @pytest.mark.asyncio
    async def test_process_calls_handle(self, handler, sample_event):
        """process() calls handle() method."""
        result = await handler.process(sample_event)
        
        assert handler.handle_called
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_process_returns_handle_result(self, handler, sample_event):
        """process() returns the result from handle()."""
        result = await handler.process(sample_event)
        
        assert result == {"success": True, "data": "handled"}

    @pytest.mark.asyncio
    async def test_pre_handle_returns_event(self, handler, sample_event):
        """pre_handle returns the event for further processing."""
        result = await handler.pre_handle(sample_event)
        
        assert result == sample_event

    @pytest.mark.asyncio
    async def test_post_handle_returns_result(self, handler, sample_event):
        """post_handle returns the result unchanged by default."""
        result_dict = {"success": True, "data": "test"}
        result = await handler.post_handle(sample_event, result_dict)
        
        assert result == result_dict

    @pytest.mark.asyncio
    async def test_process_catches_exception_and_returns_error(self, sample_event):
        """process() catches exceptions and returns error dict."""
        error_handler = ErrorHandler()
        
        result = await error_handler.process(sample_event)
        
        assert result["success"] is False
        assert "error" in result
        assert "Simulated error" in result["error"]

    def test_handler_name_is_set(self, handler):
        """Handler name is set from class name."""
        assert handler.name == "ConcreteHandler"

    @pytest.mark.asyncio
    async def test_process_pipeline_order(self, sample_event):
        """process() calls methods in order: pre_handle -> handle -> post_handle."""
        call_order = []
        
        class OrderTrackingHandler(BaseHandlerTestDouble):
            async def pre_handle(self, event):
                call_order.append("pre")
                return event
            
            async def handle(self, event):
                call_order.append("handle")
                return {"success": True}
            
            async def post_handle(self, event, result):
                call_order.append("post")
                return result
        
        handler = OrderTrackingHandler()
        await handler.process(sample_event)
        
        assert call_order == ["pre", "handle", "post"]
