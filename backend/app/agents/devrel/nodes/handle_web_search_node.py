import logging
from app.agents.shared.state import AgentState
from langchain_core.messages import HumanMessage
from ..prompts.search_prompt import EXTRACT_SEARCH_QUERY_PROMPT

logger = logging.getLogger(__name__)

async def _extract_search_query(message: str, llm) -> str:
    """Extract a concise search query from the user's message."""
    logger.info(f"Extracting search query from: {message[:100]}")
    try:
        prompt = EXTRACT_SEARCH_QUERY_PROMPT.format(message=message)
    except KeyError as e:
        logger.error(f"Missing key in EXTRACT_SEARCH_QUERY_PROMPT: {e}")
        return message  # Fallback
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    search_query = response.content.strip()
    logger.info(f"Extracted search query: {search_query}")
    return search_query

async def handle_web_search_node(state: AgentState, search_tool, llm) -> AgentState:
    """Handle web search requests"""
    logger.info(f"Handling web search for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    search_query = await _extract_search_query(latest_message, llm)
    search_results = await search_tool.search(search_query)

    state.task_result = {
        "type": "web_search",
        "query": search_query,
        "results": search_results,
        "source": "tavily_search"
    }
    state.tools_used.append("tavily_search")
    state.current_task = "web_search_handled"
    return state
