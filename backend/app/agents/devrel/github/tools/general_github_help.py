from typing import Dict, Any
import logging
from langchain_core.messages import HumanMessage
from app.agents.devrel.nodes.handlers.web_search import _extract_search_query
from .search import handle_web_search
from app.agents.devrel.github.prompts.general_github_help import GENERAL_GITHUB_HELP_PROMPT

logger = logging.getLogger(__name__)


async def handle_general_github_help(query: str, llm=None) -> Dict[str, Any]:
    """
    Execute general GitHub help using web search only (LLM removed)
    """

    logger.info("Providing general GitHub help (LLM-free mode)")

    try:
        # Extract search query safely (without LLM)
        search_result = await handle_web_search(query)

        if search_result.get("status") == "success":
            results = search_result.get("results", [])

            if not results:
                return {
                    "status": "success",
                    "sub_function": "general_github_help",
                    "query": query,
                    "response": "No relevant information found on GitHub.",
                    "message": "Provided GitHub help using web search only"
                }

            formatted = "\n\n".join(
                f"{i+1}. {r.get('title', 'No title')}\n{r.get('content', 'No content')}"
                for i, r in enumerate(results)
            )

            return {
                "status": "success",
                "sub_function": "general_github_help",
                "query": query,
                "response": f"Here are helpful GitHub resources:\n\n{formatted}",
                "message": "Provided GitHub help using web search only"
            }

        return {
            "status": "success",
            "sub_function": "general_github_help",
            "query": query,
            "response": "No search results available.",
            "message": "Provided GitHub help (no results found)"
        }

    except Exception as e:
        logger.error(f"Error in general GitHub help: {str(e)}")
        return {
            "status": "error",
            "sub_function": "general_github_help",
            "query": query,
            "error": str(e),
            "message": "Failed to provide GitHub help"
        }