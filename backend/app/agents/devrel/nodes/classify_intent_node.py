import logging
from app.agents.shared.state import AgentState
from app.agents.shared.classification_router import ClassificationRouter
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

async def classify_intent_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> AgentState:
    """Classify the user's intent and needs"""
    logger.info(f"Classifying intent for session {state.session_id}")

    # Get the latest message
    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    # Use classification router
    router = ClassificationRouter(llm)

    classification = await router.classify_message(latest_message, state.context)

    # Update state with classification
    state.context.update({
        "classification": classification,
        "intent": classification["category"],
        "priority": classification["priority"]
    })

    state.current_task = "intent_classified"
    return state
