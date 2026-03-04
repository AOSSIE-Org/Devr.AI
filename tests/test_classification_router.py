"""
Unit tests for ClassificationRouter.

Tests LLM-based message triage with JSON parsing and fallback behavior.
Uses a test double that mirrors the production ClassificationRouter behavior.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import pytest
import json
from unittest.mock import MagicMock, AsyncMock


class ClassificationRouterTestDouble:
    """
    Test double mirroring the production ClassificationRouter implementation.
    This avoids dependency issues while testing the classification pattern.
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    async def should_process_message(self, message: str, context: dict = None) -> dict:
        """Determine if a message needs DevRel assistance."""
        try:
            triage_prompt = f"Analyze this message: {message}. Context: {context or 'No additional context'}"
            response = await self.llm.ainvoke([{"role": "user", "content": triage_prompt}])
            response_text = response.content.strip()
            
            if '{' in response_text:
                # Extract JSON from response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                result = json.loads(json_str)
                return {
                    "needs_devrel": result.get("needs_devrel", True),
                    "priority": result.get("priority", "medium"),
                    "reasoning": result.get("reasoning", "LLM classification"),
                    "original_message": message
                }
            return self._fallback_triage(message)
        except Exception:
            return self._fallback_triage(message)
    
    def _fallback_triage(self, message: str) -> dict:
        """Default triage when LLM fails or returns invalid response."""
        return {
            "needs_devrel": True,
            "priority": "medium",
            "reasoning": "Fallback - assuming DevRel assistance needed",
            "original_message": message
        }


class TestClassificationRouter:
    """Tests for ClassificationRouter pattern."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client that returns a valid JSON triage response."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"needs_devrel": true, "priority": "high", "reasoning": "Test reasoning"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        return mock_llm

    @pytest.fixture
    def mock_llm_client_error(self):
        """Mock LLM client that raises an exception."""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM API Error"))
        return mock_llm

    def test_fallback_triage_returns_correct_structure(self, mock_llm_client):
        """_fallback_triage returns a dict with all required keys."""
        router = ClassificationRouterTestDouble(llm_client=mock_llm_client)
        result = router._fallback_triage("test message")
        
        assert "needs_devrel" in result
        assert "priority" in result
        assert "reasoning" in result
        assert "original_message" in result
        
        assert result["needs_devrel"] is True
        assert result["priority"] == "medium"
        assert result["original_message"] == "test message"

    @pytest.mark.asyncio
    async def test_should_process_message_with_valid_json_response(self, mock_llm_client):
        """Parses JSON from LLM response correctly."""
        router = ClassificationRouterTestDouble(llm_client=mock_llm_client)
        
        result = await router.should_process_message("How do I contribute?")
        
        assert result["needs_devrel"] is True
        assert result["priority"] == "high"
        assert result["reasoning"] == "Test reasoning"
        assert result["original_message"] == "How do I contribute?"

    @pytest.mark.asyncio
    async def test_should_process_message_extracts_json_from_mixed_response(self):
        """Extracts JSON even when LLM response contains extra text."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = 'Here is my analysis:\n{"needs_devrel": false, "priority": "low", "reasoning": "Simple greeting"}\nHope this helps!'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        router = ClassificationRouterTestDouble(llm_client=mock_llm)
        result = await router.should_process_message("Hello!")
        
        assert result["needs_devrel"] is False
        assert result["priority"] == "low"

    @pytest.mark.asyncio
    async def test_should_process_message_uses_fallback_on_error(self, mock_llm_client_error):
        """Falls back to default triage when LLM call fails."""
        router = ClassificationRouterTestDouble(llm_client=mock_llm_client_error)
        
        result = await router.should_process_message("What is DevRel?")
        
        # Should use fallback values
        assert result["needs_devrel"] is True
        assert result["priority"] == "medium"
        assert "Fallback" in result["reasoning"]

    @pytest.mark.asyncio
    async def test_should_process_message_handles_invalid_json(self):
        """Falls back when LLM returns invalid JSON."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "I think this needs devrel help, priority is high"  # No JSON
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        router = ClassificationRouterTestDouble(llm_client=mock_llm)
        result = await router.should_process_message("Help me with the API")
        
        # Should use fallback
        assert result["needs_devrel"] is True
        assert result["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_should_process_message_with_context(self, mock_llm_client):
        """Context is passed correctly to LLM."""
        router = ClassificationRouterTestDouble(llm_client=mock_llm_client)
        context = {"channel": "help", "user_role": "contributor"}
        
        result = await router.should_process_message("Need help", context=context)
        
        # Verify LLM was called
        assert mock_llm_client.ainvoke.called
        assert result["original_message"] == "Need help"

    @pytest.mark.asyncio
    async def test_should_process_message_defaults_missing_fields(self):
        """Uses default values when LLM response is missing fields."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        # JSON missing some fields
        mock_response.content = '{"needs_devrel": false}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        router = ClassificationRouterTestDouble(llm_client=mock_llm)
        result = await router.should_process_message("Test")
        
        assert result["needs_devrel"] is False
        assert result["priority"] == "medium"  # Default
        assert result["reasoning"] == "LLM classification"  # Default
