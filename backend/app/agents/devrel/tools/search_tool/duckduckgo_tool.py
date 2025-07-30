import logging
from ddgs import DDGS

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool:
    async def search(self, query: str) -> str:
        logger.info(f"Performing DuckDuckGo search for: {query}")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                logger.info("No search results found")
                return "No search results found."

            # Format results for the agent
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'content': result.get('body', ''),
                    'url': result.get('href', '')
                })

            return str(formatted_results)

        except ConnectionError as e:
            logger.error(f"Network error during search: {e}")
            return f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return f"Search failed: {str(e)}"
