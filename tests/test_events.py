"""
Unit tests for BaseEvent.

Tests event creation, serialization, and deserialization.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import pytest
from datetime import datetime
from app.core.events.base import BaseEvent
from app.core.events.enums import EventType, PlatformType


class TestBaseEvent:
    """Tests for BaseEvent class."""

    @pytest.fixture
    def minimal_event(self):
        """Minimal valid event."""
        return BaseEvent(
            id="evt-001",
            platform="discord",
            event_type="message.created",
            actor_id="user-123"
        )

    @pytest.fixture
    def full_event(self):
        """Event with all fields populated."""
        return BaseEvent(
            id="evt-002",
            platform="github",
            event_type="issue.created",
            actor_id="user-456",
            actor_name="TestUser",
            channel_id="repo-123",
            content="Issue description here",
            raw_data={"original": "payload", "number": 42},
            metadata={"source": "webhook", "priority": "high"}
        )

    # ------------------------------------------------------------------
    # Creation tests
    # ------------------------------------------------------------------

    def test_creation_with_required_fields(self, minimal_event):
        """Event can be created with only required fields."""
        assert minimal_event.id == "evt-001"
        assert minimal_event.platform == "discord"
        assert minimal_event.event_type == "message.created"
        assert minimal_event.actor_id == "user-123"

    def test_creation_with_all_fields(self, full_event):
        """Event can be created with all fields."""
        assert full_event.id == "evt-002"
        assert full_event.platform == "github"
        assert full_event.actor_name == "TestUser"
        assert full_event.content == "Issue description here"
        assert full_event.raw_data["number"] == 42
        assert full_event.metadata["priority"] == "high"

    def test_default_values(self, minimal_event):
        """Default values are set correctly."""
        assert minimal_event.actor_name is None
        assert minimal_event.channel_id is None
        assert minimal_event.content is None
        assert minimal_event.raw_data == {}
        assert minimal_event.metadata == {}

    def test_timestamp_has_default(self, minimal_event):
        """Timestamp is automatically set."""
        assert isinstance(minimal_event.timestamp, datetime)

    def test_enum_platform_values(self):
        """Events accept PlatformType enum values."""
        event = BaseEvent(
            id="evt-enum",
            platform=PlatformType.DISCORD,
            event_type=EventType.MESSAGE_CREATED,
            actor_id="user-789"
        )
        
        assert event.platform == PlatformType.DISCORD
        assert event.event_type == EventType.MESSAGE_CREATED

    # ------------------------------------------------------------------
    # Serialization tests
    # ------------------------------------------------------------------

    def test_to_dict_returns_dict(self, full_event):
        """to_dict() returns a dictionary."""
        result = full_event.to_dict()
        
        assert isinstance(result, dict)

    def test_to_dict_contains_all_fields(self, full_event):
        """to_dict() contains all event fields."""
        result = full_event.to_dict()
        
        assert result["id"] == "evt-002"
        assert result["platform"] == "github"
        assert result["event_type"] == "issue.created"
        assert result["actor_id"] == "user-456"
        assert result["actor_name"] == "TestUser"
        assert result["content"] == "Issue description here"
        assert "timestamp" in result

    def test_to_dict_preserves_raw_data(self, full_event):
        """to_dict() preserves raw_data structure."""
        result = full_event.to_dict()
        
        assert result["raw_data"] == {"original": "payload", "number": 42}

    def test_to_dict_preserves_metadata(self, full_event):
        """to_dict() preserves metadata structure."""
        result = full_event.to_dict()
        
        assert result["metadata"] == {"source": "webhook", "priority": "high"}

    # ------------------------------------------------------------------
    # Deserialization tests
    # ------------------------------------------------------------------

    def test_from_dict_creates_event(self):
        """from_dict() creates an event from dictionary."""
        data = {
            "id": "evt-from-dict",
            "platform": "slack",
            "event_type": "message.created",
            "actor_id": "user-999",
            "content": "Hello from dict"
        }
        
        event = BaseEvent.from_dict(data)
        
        assert isinstance(event, BaseEvent)
        assert event.id == "evt-from-dict"
        assert event.platform == "slack"
        assert event.content == "Hello from dict"

    def test_from_dict_with_all_fields(self):
        """from_dict() handles all fields correctly."""
        now = datetime.now()
        data = {
            "id": "evt-full",
            "platform": "github",
            "event_type": "pr.created",
            "timestamp": now,
            "actor_id": "user-full",
            "actor_name": "FullUser",
            "channel_id": "repo-full",
            "content": "PR content",
            "raw_data": {"pr_number": 123},
            "metadata": {"label": "enhancement"}
        }
        
        event = BaseEvent.from_dict(data)
        
        assert event.actor_name == "FullUser"
        assert event.raw_data["pr_number"] == 123
        assert event.metadata["label"] == "enhancement"

    # ------------------------------------------------------------------
    # Round-trip tests
    # ------------------------------------------------------------------

    def test_round_trip_serialization(self, full_event):
        """Event survives to_dict -> from_dict round trip."""
        dict_repr = full_event.to_dict()
        restored = BaseEvent.from_dict(dict_repr)
        
        assert restored.id == full_event.id
        assert restored.platform == full_event.platform
        assert restored.event_type == full_event.event_type
        assert restored.actor_id == full_event.actor_id
        assert restored.content == full_event.content
        assert restored.raw_data == full_event.raw_data
        assert restored.metadata == full_event.metadata

    def test_minimal_event_round_trip(self, minimal_event):
        """Minimal event survives round trip."""
        dict_repr = minimal_event.to_dict()
        restored = BaseEvent.from_dict(dict_repr)
        
        assert restored.id == minimal_event.id
        assert restored.actor_id == minimal_event.actor_id
