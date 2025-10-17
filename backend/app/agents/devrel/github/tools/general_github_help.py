from typing import Dict, Any
import logging
from langchain_core.messages import HumanMessage
from app.agents.devrel.nodes.handlers.web_search import _extract_search_query
from .search import handle_web_search
from app.agents.devrel.github.prompts.general_github_help import GENERAL_GITHUB_HELP_PROMPT

logger = logging.getLogger(__name__)


async def handle_general_github_help(query: str, llm) -> Dict[str, Any]:
    """Execute general GitHub help with web search and LLM knowledge"""
    logger.info("Providing general GitHub help")

    try:
        query = await _extract_search_query(query, llm)
        search_result = await handle_web_search(query)

        if search_result.get("status") == "success":
            search_context = "SEARCH RESULTS:\n"
            for result in search_result.get("results", []):
                search_context += f"- {result.get('title', 'No title')}: {result.get('content', 'No content')}\n"
        else:
            search_context = "No search results available."

        help_prompt = GENERAL_GITHUB_HELP_PROMPT.format(
            query=query,
            search_context=search_context
        )

        response = await llm.ainvoke([HumanMessage(content=help_prompt)])

        return {
            "status": "success",
            "sub_function": "general_github_help",
            "query": query,
            "response": response.content.strip(),
            "search_context": search_context,
            "message": "Provided GitHub help using LLM expertise and web search"
        }

    except Exception as e:
        logger.error(f"Error in general GitHub help: {str(e)}")
        return {
            "status": "error",
            "sub_function": "general_github_help",
            "query": query,
            "error": str(e),
            "message": "Failed to provide general GitHub help"
        }