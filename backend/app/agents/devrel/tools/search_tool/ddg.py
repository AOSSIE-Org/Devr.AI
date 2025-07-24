import asyncio
import logging
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
from langchain.tools import BaseTool
from langsmith import traceable

logger = logging.getLogger(__name__)


class DuckDuckGoSearchTool:
    """DDGS-based DuckDuckGo search integration (internal helper)"""

    def _perform_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        with DDGS() as ddg:
            return list(ddg.text(query, max_results=max_results))

    @traceable(name="duckduckgo_search_tool", run_type="tool")
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        try:
            response = await asyncio.to_thread(
                self._perform_search, query, max_results
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


class DuckDuckGoSearchLangTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = (
        "Useful for when you need to answer questions about current events or general world knowledge. "
        "Input should be a search query."
    )

    def __init__(self):
        super().__init__()
        self.tool = DuckDuckGoSearchTool()

    def _run(self, query: str, max_results: Optional[int] = 5) -> Any:
        """Used in non-async mode"""
        return asyncio.run(self.tool.search(query, max_results))

    async def _arun(self, query: str, max_results: Optional[int] = 5) -> Any:
        """Used by LangGraph or async chains"""
        return await self.tool.search(query, max_results)
