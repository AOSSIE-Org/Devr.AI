import sys
import os
import pytest
from unittest.mock import MagicMock, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.classification.classification_router import ClassificationRouter


@pytest.mark.asyncio
async def test_classification_fallback_on_error():
    """Test that classification fallback returns needs_devrel: False when LLM raises an exception"""
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(side_effect=Exception("API rate limit"))
    router = ClassificationRouter(llm_client=mock_llm)

    result = await router.should_process_message("test message")

    assert result["needs_devrel"] is False
    assert result["priority"] == "low"
    assert "Fallback" in result["reasoning"]


@pytest.mark.asyncio
async def test_classification_fallback_on_invalid_json():
    """Test that classification fallback handles invalid JSON response from LLM"""
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=MagicMock(content="This is not valid JSON at all")
    )
    router = ClassificationRouter(llm_client=mock_llm)

    result = await router.should_process_message("test message")

    assert result["needs_devrel"] is False
    assert result["priority"] == "low"
    assert "Fallback" in result["reasoning"]