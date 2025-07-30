import logging
from typing import Dict, Any
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage
from app.agents.devrel.prompts.search_prompt import EXTRACT_SEARCH_QUERY_PROMPT

logger = logging.getLogger(__name__)

async def _extract_search_query(message: str, llm) -> str:
    """
    Extract a concise search query from the user's message by invoking the LLM.
    """
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

async def handle_web_search_node(state: AgentState, search_tool, llm) -> dict:
    """
    Handle web search requests
    """
    logger.info(f"Handling web search for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    search_query = await _extract_search_query(latest_message, llm)

    # Fix: Use arun() instead of search()
    search_results = await search_tool.arun(search_query)

    return {
        "task_result": {
            "type": "web_search",
            "query": search_query,
            "results": search_results,
            "source": "duckduckgo_search"
        },
        "tools_used": ["duckduckgo_search"],
        "current_task": "web_search_handled"
    }

def create_search_response(task_result: Dict[str, Any]) -> str:
    """
    Create a user-friendly response string from search results.
    """

    query = task_result.get("query")
    results = task_result.get("results", [])

    if not results:
        return f"I couldn't find any information for '{query}'. You might want to try rephrasing your search."

    response_parts = [f"Here's what I found for '{query}':"]
    for i, result in enumerate(results[:5]):
        title = result.get('title', 'N/A')
        snippet = result.get('content', 'N/A')
        url = result.get('url', '#')
        response_parts.append(f"{i+1}. {title}: {snippet}")
        response_parts.append(f"   (Source: {url})")

    response_parts.append("You can ask me to search again with a different query if these aren't helpful.")
    return "\n".join(response_parts)
