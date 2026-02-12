import asyncio
import logging
import random
from typing import List, Dict, Any
from ddgs import DDGS
from langsmith import traceable

logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool:
    """DDGS-based DuckDuckGo search integration with configurable options.
    
    Args:
        timeout: Timeout for search requests in seconds (default: 10)
        max_retries: Maximum number of retry attempts on failure (default: 2)
        cache_enabled: Enable caching of search results (default: False)
        base_delay: Base delay for exponential backoff in seconds (default: 1)
        max_delay: Maximum delay between retries in seconds (default: 10)
    """

    def __init__(self, timeout: int = 10, max_retries: int = 2, cache_enabled: bool = False, 
                 base_delay: float = 1.0, max_delay: float = 10.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_enabled = cache_enabled
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._cache: dict = {} if cache_enabled else None
        logger.info(f"Initialized DuckDuckGoSearchTool (timeout={timeout}s, retries={max_retries}, cache={cache_enabled})")

    def _perform_search(self, query: str, max_results: int):
        with DDGS() as ddg:
            return ddg.text(query, max_results=max_results)
        
    @traceable(name="duckduckgo_search_tool", run_type="tool")
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform a DuckDuckGo search with caching and retry logic.
        
        Args:
            query: The search query string
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            List of search results with title, content, URL, and score
        """
        # Check cache if enabled
        cache_key = f"{query}:{max_results}"
        if self.cache_enabled and cache_key in self._cache:
            logger.debug(f"Returning cached results for query: {query}")
            return self._cache[cache_key]
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Search attempt {attempt + 1}/{self.max_retries + 1} for query: {query}")
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._perform_search, 
                        query=query, 
                        max_results=max_results
                    ),
                    timeout=self.timeout
                )
            
                results = []
                for result in response or []:
                    results.append({
                        "title": result.get("title", ""),
                        "content": result.get("body", ""),
                        "url": result.get("href", ""),
                        "score": 0
                    })
                
                # Cache results if enabled
                if self.cache_enabled:
                    self._cache[cache_key] = results
                    logger.debug(f"Cached {len(results)} results for query: {query}")
                
                logger.info(f"Successfully retrieved {len(results)} results for query: {query}")
                return results
            
            except (asyncio.TimeoutError, TimeoutError):
                last_exception = TimeoutError(f"Search timed out after {self.timeout}s")
                logger.warning(f"Search timeout (attempt {attempt + 1}/{self.max_retries + 1}): {query}")
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(-0.1, 0.1), self.max_delay)
                    await asyncio.sleep(delay)
                continue
            
            except ConnectionError as e:
                last_exception = e
                logger.warning(f"Network issue (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(-0.1, 0.1), self.max_delay)
                    await asyncio.sleep(delay)
                continue
            
            except Exception as e:
                last_exception = e
                logger.error(f"Search error (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}")
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (2 ** attempt) + random.uniform(-0.1, 0.1), self.max_delay)
                    await asyncio.sleep(delay)
                continue
        
        # All retries failed
        logger.error(f"All {self.max_retries + 1} search attempts failed for query: {query}. Last error: {last_exception}")
        return []
