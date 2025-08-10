import asyncio
import logging
from typing import List, Dict, Any
from ddgs import DDGS
from langsmith import traceable

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool:
    """DDGS-based DuckDuckGo search integration"""

    def __init__(self):
        pass

    def _perform_search(self, query: str, max_results: int):
        with DDGS() as ddg:
            return ddg.text(query, max_results=max_results)

    @traceable(name="duckduckgo_search_tool", run_type="tool")
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        try:
            response = await asyncio.to_thread(
                self._perform_search,
                query=query,
                max_results=max_results
            )

            results = []
            for result in response or []:
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("body", ""),
                    "url": result.get("href", ""),
                    "score": 0
                })
            return results

        except (ConnectionError, TimeoutError) as e:
            logger.warning("Network issue during DDG search: %s", e)
            return []
        except Exception as e:
            logger.error("DuckDuckGo search failed: %s", str(e))
            return []
