"""
Shared pytest fixtures for Devr.AI backend tests.
"""
import sys
import os
from datetime import datetime
from typing import Dict, Any
from unittest.mock import MagicMock, AsyncMock

import pytest

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))


# ---------------------------------------------------------------------------
# Event fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_event_data() -> Dict[str, Any]:
    """Returns minimal valid data for creating a BaseEvent."""
    return {
        "id": "evt-12345",
        "platform": "discord",
        "event_type": "message.created",
        "actor_id": "user-001",
        "actor_name": "TestUser",
        "channel_id": "chan-001",
        "content": "Hello, how do I contribute?",
        "raw_data": {"original": "payload"},
        "metadata": {"source": "test"},
    }


@pytest.fixture
def sample_faq_event_data(sample_event_data) -> Dict[str, Any]:
    """Event data for a FAQ request."""
    data = sample_event_data.copy()
    data["event_type"] = "faq.requested"
    data["content"] = "what is devr.ai?"
    return data


# ---------------------------------------------------------------------------
# Handler fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_discord_bot():
    """Mock Discord bot with channel sending capability."""
    bot = MagicMock()
    channel = MagicMock()
    channel.send = AsyncMock()
    bot.get_channel = MagicMock(return_value=channel)
    return bot


# ---------------------------------------------------------------------------
# LLM fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_llm_client():
    """Mock LLM client that returns a valid JSON triage response."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = '{"needs_devrel": true, "priority": "high", "reasoning": "Test reasoning"}'
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)
    return mock_llm


@pytest.fixture
def mock_llm_client_error():
    """Mock LLM client that raises an exception."""
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM API Error"))
    return mock_llm
