import logging
from typing import Dict, Any
from app.agents.devrel.tools.search_tool import TavilySearchTool
logger = logging.getLogger(__name__)


async def handle_web_search(query: str) -> Dict[str, Any]:
    """Handle web search using Tavily search tool"""
    logger.info("Handling web search request")

    try:
        search_tool = TavilySearchTool()
        search_results = await search_tool.search(query, max_results=5)

        if not search_results:
            return {
                "status": "no_results",
                "sub_function": "web_search",
                "query": query,
                "message": "No web search results found for the query",
                "results": []
            }

        return {
            "status": "success",
            "sub_function": "web_search",
            "query": query,
            "results": search_results,
            "total_results": len(search_results),
            "message": f"Found {len(search_results)} web search results"
        }

    except Exception as e:
        logger.error(f"Error in web search: {str(e)}")
        return {
            "status": "error",
            "sub_function": "web_search",
            "query": query,
            "error": str(e),
            "message": "Failed to perform web search"
        }
