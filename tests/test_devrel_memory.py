"""Unit tests for DevRel Agent memory persistence and context gathering nodes."""
pytest_plugins = ('pytest_asyncio',)

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.agents.state import AgentState
from app.agents.devrel.nodes.gather_context import gather_context_node
from app.agents.devrel.nodes.summarization import (
    summarize_conversation_node,
    store_summary_to_database,
)




def _create_test_state(**overrides) -> AgentState:
    """Create a baseline AgentState instance for testing memory nodes."""
    base_data = {
        "session_id": "test-session-123",
        "user_id": "discord-user-456",
        "platform": "discord",
        "messages": [
            {"role": "user", "content": "Hello Devr.AI"},
            {"role": "assistant", "content": "Hi! How can I help you contribute today?"},
        ],
        "context": {
            "original_message": "Can you help me find an issue?",
            "author": {
                "id": "discord-user-456",
                "username": "gsoc_contributor",
                "display_name": "GSoC Contributor",
            },
            "user_uuid": "uuid-1234-5678",
        },
        "user_profile": {"username": "gsoc_contributor", "skills": ["python"]},
        "interaction_count": 15,
        "conversation_summary": "Initial conversation summary.",
        "key_topics": ["onboarding"],
    }
    base_data.update(overrides)
    return AgentState(**base_data)


@pytest.mark.asyncio
async def test_gather_context_preserves_user_profile_for_returning_user():
    """Verify that gather_context_node retains user_profile when loading previous DB context."""
    state = _create_test_state(conversation_summary="", key_topics=[])

    mock_user = MagicMock()
    mock_user.model_dump.return_value = {
        "discord_id": "discord-user-456",
        "discord_username": "gsoc_contributor",
        "display_name": "GSoC Contributor",
    }

    prev_db_context = {
        "conversation_summary": "Previously discussed LangGraph memory bugs.",
        "key_topics": ["langgraph", "supabase"],
        "total_interactions": 15,
    }

    with patch(
        "app.agents.devrel.nodes.gather_context.ensure_user_exists",
        new=AsyncMock(return_value="uuid-1234-5678"),
    ), patch(
        "app.agents.devrel.nodes.gather_context.get_or_create_user_by_discord",
        new=AsyncMock(return_value=mock_user),
    ), patch(
        "app.agents.devrel.nodes.gather_context.get_conversation_context",
        new=AsyncMock(return_value=prev_db_context),
    ):
        result = await gather_context_node(state)

    assert result["conversation_summary"] == "Previously discussed LangGraph memory bugs."
    assert result["key_topics"] == ["langgraph", "supabase"]
    assert "user_profile" in result
    assert result["user_profile"]["discord_username"] == "gsoc_contributor"


@pytest.mark.asyncio
async def test_summarize_conversation_node_persists_to_database():
    """Verify that summarize_conversation_node calls store_summary_to_database before resetting count."""
    state = _create_test_state(interaction_count=15)

    mock_llm = MagicMock()
    mock_summary_response = MagicMock()
    mock_summary_response.content = "Updated summary of contributor progress."
    mock_topics_response = MagicMock()
    mock_topics_response.content = "langgraph, pytest, memory"
    mock_llm.ainvoke = AsyncMock(side_effect=[mock_summary_response, mock_topics_response])

    with patch(
        "app.agents.devrel.nodes.summarization.store_summary_to_database",
        new=AsyncMock(),
    ) as mock_store_db:
        result = await summarize_conversation_node(state, mock_llm)

        mock_store_db.assert_awaited_once()
        persisted_state = mock_store_db.call_args[0][0]
        assert persisted_state.conversation_summary == "Updated summary of contributor progress."
        assert persisted_state.key_topics == ["langgraph", "pytest", "memory"]
        assert persisted_state.interaction_count == 15

    assert result["conversation_summary"] == "Updated summary of contributor progress."
    assert result["interaction_count"] == -15
    assert result["summarization_needed"] is False


@pytest.mark.asyncio
async def test_store_summary_accumulates_total_interactions():
    """Verify that store_summary_to_database adds current interaction_count to existing DB total."""
    state = _create_test_state(
        interaction_count=15,
        conversation_summary="Cumulative summary.",
        key_topics=["langgraph", "supabase"],
    )

    mock_select_response = MagicMock()
    mock_select_response.data = [{"total_interactions": 30}]

    mock_upsert_response = MagicMock()
    mock_upsert_response.data = [{"user_id": "uuid-1234-5678"}]

    mock_table = MagicMock()
    mock_table.select.return_value.eq.return_value.limit.return_value.execute = AsyncMock(
        return_value=mock_select_response
    )
    mock_table.upsert.return_value.execute = AsyncMock(return_value=mock_upsert_response)

    with patch("app.agents.devrel.nodes.summarization.supabase") as mock_supabase:
        mock_supabase.table.return_value = mock_table
        await store_summary_to_database(state)

    mock_table.upsert.assert_called_once()
    upserted_record = mock_table.upsert.call_args[0][0]
    assert upserted_record["user_id"] == "uuid-1234-5678"
    assert upserted_record["total_interactions"] == 45
    assert upserted_record["conversation_summary"] == "Cumulative summary."