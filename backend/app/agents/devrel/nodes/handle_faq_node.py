import logging
from app.agents.shared.state import AgentState

logger = logging.getLogger(__name__)

async def handle_faq_node(state: AgentState, faq_tool) -> AgentState:
    """Handle FAQ requests"""
    logger.info(f"Handling FAQ for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    # faq_tool will be passed from the agent, similar to llm for classify_intent
    faq_response = await faq_tool.get_response(latest_message)

    state.task_result = {
        "type": "faq",
        "response": faq_response,
        "source": "faq_database"
    }

    state.current_task = "faq_handled"
    return state
