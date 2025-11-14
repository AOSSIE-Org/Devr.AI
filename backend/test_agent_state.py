import pytest
from app.agents.state import AgentState 

def test_hil_fields_in_agent_state():
    """
    Tests that the new HIL fields exist in AgentState,
    have correct defaults, and can be updated.
    """
    try:
        state = AgentState(
            session_id="test_session",
            user_id="test_user",
            platform="test"
        )
    except Exception as e:
        pytest.fail(f"Failed to instantiate AgentState: {e}")

    assert state.waiting_for_human_input is False, "Default waiting_for_human_input should be False"
    assert state.hil_message is None, "Default hil_message should be None"

    assert state.requires_human_review is False, "Default requires_human_review should be False"
    assert state.human_feedback is None, "Default human_feedback should be None"

    state.waiting_for_human_input = True
    state.hil_message = "This is a test HIL question"

    assert state.waiting_for_human_input is True, "waiting_for_human_input should be True after setting"
    assert state.hil_message == "This is a test HIL question", "hil_message should be updated"

    print("\n✅ test_hil_fields_in_agent_state: Passed")