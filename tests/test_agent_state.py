"""
Unit tests for AgentState.

Tests Pydantic state model, default values, and reducer functions.
"""
import sys
import os

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

import pytest
from datetime import datetime

# Import directly from the state module to avoid agents/__init__.py
# which imports DevRelAgent and requires langgraph
import importlib.util
state_path = os.path.join(backend_path, 'app', 'agents', 'state.py')
spec = importlib.util.spec_from_file_location("state", state_path)
state_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state_module)
AgentState = state_module.AgentState
replace_summary = state_module.replace_summary
replace_topics = state_module.replace_topics


class TestReducerFunctions:
    """Tests for state reducer functions."""

    def test_replace_summary_with_new_value(self):
        """New value replaces existing."""
        result = replace_summary("old summary", "new summary")
        assert result == "new summary"

    def test_replace_summary_keeps_existing_when_new_is_none(self):
        """Keeps existing when new is None."""
        result = replace_summary("old summary", None)
        assert result == "old summary"

    def test_replace_summary_both_none(self):
        """Returns None when both are None."""
        result = replace_summary(None, None)
        assert result is None

    def test_replace_topics_with_new_list(self):
        """New list replaces existing."""
        result = replace_topics(["old"], ["new1", "new2"])
        assert result == ["new1", "new2"]

    def test_replace_topics_keeps_existing_when_new_empty(self):
        """Keeps existing when new is empty list."""
        result = replace_topics(["existing"], [])
        assert result == ["existing"]

    def test_replace_topics_both_empty(self):
        """Returns existing empty list when both empty."""
        result = replace_topics([], [])
        assert result == []


class TestAgentState:
    """Tests for AgentState class."""

    @pytest.fixture
    def minimal_state(self):
        """Minimal valid state."""
        return AgentState(
            session_id="sess-001",
            user_id="user-001",
            platform="discord"
        )

    def test_creation_with_required_fields(self, minimal_state):
        """State can be created with only required fields."""
        assert minimal_state.session_id == "sess-001"
        assert minimal_state.user_id == "user-001"
        assert minimal_state.platform == "discord"

    def test_default_values_set(self, minimal_state):
        """Default values are set correctly."""
        assert minimal_state.messages == []
        assert minimal_state.context == {}
        assert minimal_state.errors == []
        assert minimal_state.retry_count == 0
        assert minimal_state.max_retries == 3
        assert minimal_state.requires_human_review is False
        assert minimal_state.summarization_needed is False

    def test_default_datetime_fields(self, minimal_state):
        """Datetime fields have default values."""
        assert isinstance(minimal_state.session_start_time, datetime)
        assert isinstance(minimal_state.last_interaction_time, datetime)

    def test_optional_fields_default_none(self, minimal_state):
        """Optional fields default to None."""
        assert minimal_state.current_task is None
        assert minimal_state.task_result is None
        assert minimal_state.next_action is None
        assert minimal_state.human_feedback is None
        assert minimal_state.thread_id is None
        assert minimal_state.channel_id is None
        assert minimal_state.final_response is None
        assert minimal_state.conversation_summary is None

    def test_custom_values_override_defaults(self):
        """Custom values override defaults."""
        state = AgentState(
            session_id="sess-002",
            user_id="user-002",
            platform="slack",
            max_retries=5,
            requires_human_review=True,
            channel_id="channel-123"
        )
        
        assert state.max_retries == 5
        assert state.requires_human_review is True
        assert state.channel_id == "channel-123"

    def test_model_dump_serialization(self, minimal_state):
        """State can be serialized with model_dump."""
        dumped = minimal_state.model_dump()
        
        assert isinstance(dumped, dict)
        assert dumped["session_id"] == "sess-001"
        assert dumped["user_id"] == "user-001"
        assert "messages" in dumped
        assert "errors" in dumped

    def test_state_from_dict(self):
        """State can be created from dictionary."""
        data = {
            "session_id": "sess-003",
            "user_id": "user-003",
            "platform": "github",
            "messages": [{"role": "user", "content": "Hello"}],
            "key_topics": ["python", "testing"]
        }
        
        state = AgentState(**data)
        
        assert state.session_id == "sess-003"
        assert len(state.messages) == 1
        assert state.key_topics == ["python", "testing"]

    def test_list_fields_are_mutable(self):
        """List fields can be modified."""
        state = AgentState(
            session_id="sess-004",
            user_id="user-004",
            platform="discord"
        )
        
        state.messages.append({"role": "user", "content": "test"})
        state.errors.append("test error")
        state.tools_used.append("search")
        
        assert len(state.messages) == 1
        assert len(state.errors) == 1
        assert len(state.tools_used) == 1

    def test_dict_fields_are_mutable(self):
        """Dict fields can be modified."""
        state = AgentState(
            session_id="sess-005",
            user_id="user-005",
            platform="discord"
        )
        
        state.context["key"] = "value"
        state.user_profile["name"] = "Test User"
        
        assert state.context["key"] == "value"
        assert state.user_profile["name"] == "Test User"

    def test_interaction_count_starts_at_zero(self, minimal_state):
        """Interaction count defaults to 0."""
        assert minimal_state.interaction_count == 0

    def test_onboarding_state_default_empty(self, minimal_state):
        """Onboarding state defaults to empty dict."""
        assert minimal_state.onboarding_state == {}

    def test_arbitrary_types_allowed(self):
        """Config allows arbitrary types."""
        # This verifies the model_config setting works
        state = AgentState(
            session_id="sess-006",
            user_id="user-006",
            platform="discord",
            session_start_time=datetime.now()
        )
        assert isinstance(state.session_start_time, datetime)
