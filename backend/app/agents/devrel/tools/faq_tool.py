import logging
import asyncio
from typing import Optional, Any, Dict, List
from pathlib import Path
from langchain_core.messages import HumanMessage
from app.agents.state import AgentState
from app.core.config.settings import settings as app_settings

logger = logging.getLogger(__name__)

ORG_NAME = app_settings.org_name
OFFICIAL_HANDLES = [
    app_settings.org_website,
    app_settings.org_github,
    app_settings.org_twitter,
]
FAQ_SEARCH_TIMEOUT = getattr(app_settings, "faq_search_timeout", 10.0)
FAQ_LLM_TIMEOUT = getattr(app_settings, "faq_llm_timeout", 15.0)

# Path to FAQ prompts
FAQ_PROMPTS_PATH = Path(__file__).parent / "prompt" / "faq_prompt.py"

def load_prompt(name: str) -> str:
    """
    Load a prompt from a .txt file or fallback to faq_prompt.py.
    """
    prompt_path = FAQ_PROMPTS_PATH / f"{name}.txt"

    # 1. Try to load from text file
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    # 2. Fallback: Load from Python module
    try:
        from app.agents.devrel.prompts.faq_prompt import REFINEMENT_PROMPT
        return getattr(REFINEMENT_PROMPT, name)
    except (ImportError, AttributeError):
        raise FileNotFoundError(
            f"Prompt '{name}' not found in {prompt_path} or faq_prompt.py"
        )


class FAQTool:
    """
    Dynamic FAQ handling tool integrating search and LLM synthesis.
    Handles FAQ queries by refining search terms, fetching relevant data,
    and synthesizing coherent responses with source citations.
    """

    def __init__(self, search_tool: Any, llm: Any):
        self.search_tool = search_tool
        self.llm = llm

    async def get_response(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """
        Fetch and synthesize a dynamic FAQ response using web search and LLM.
        """
        logger.info(f"Handling FAQ for session {state.session_id}")

        # Extract latest user message
        latest_message = (
            state.messages[-1].get("content", "")
            if state.messages
            else state.context.get("original_message", "")
        )

        if not latest_message:
            logger.warning("[FAQ_TOOL] Empty user message — returning fallback")
            return {
                "task_result": {
                    "type": "faq",
                    "response": self._generate_fallback_response(latest_message),
                    "source": "dynamic_web_search",
                },
                "current_task": "faq_handled",
            }

        try:
            # Build site filters from official handles
            site_filters = self._build_site_filters()
            logger.info(f"[FAQ_TOOL] Using site filters: {site_filters or '(none)'}")

            # Process FAQ request
            faq_response = await self._dynamic_faq_process(
                latest_message, site_filters=site_filters
            )

            return {
                "task_result": {
                    "type": "faq",
                    "response": faq_response,
                    "source": "dynamic_web_search",
                },
                "current_task": "faq_handled",
            }

        except Exception as e:
            logger.error(f"[FAQ_TOOL] Failed to handle FAQ: {e}")
            return {
                "task_result": {
                    "type": "faq",
                    "response": f"Sorry, something went wrong while handling your FAQ request: {e}",
                    "source": "error",
                },
                "current_task": "faq_failed",
            }


    def _build_site_filters(self) -> str:
        """Construct search site filters from official handles."""
        from urllib.parse import urlparse

        domains = []
        for u in OFFICIAL_HANDLES:
            try:
                parsed = urlparse(u)
                domain = parsed.netloc or parsed.path
                if domain:
                    domains.append(domain)
            except Exception:
                continue

        return " OR ".join([f"site:{d}" for d in domains]) if domains else ""


    async def _dynamic_faq_process(self, message: str, site_filters: str = "") -> str:
        """
        Pipeline: refine → search → synthesize → format
        """
        try:
            # Step 1: Refine the query
            logger.debug(f"[FAQ_TOOL] Refining query for org '{ORG_NAME}'")
            refined_query = await self._refine_faq_query(message)

            if site_filters:
                refined_query = f"({refined_query}) AND ({site_filters})"
            logger.debug(f"[FAQ_TOOL] Final query: {refined_query}")

            # Step 2: Search
            logger.info(f"[FAQ_TOOL] Searching for: {refined_query}")
            try:
                search_results = await asyncio.wait_for(
                    self.search_tool.search(refined_query), timeout=FAQ_SEARCH_TIMEOUT
                )
            except Exception as err:
                logger.error(f"[FAQ_TOOL] Search failed: {err}")
                return self._generate_fallback_response(message)

            if not search_results:
                logger.warning(f"[FAQ_TOOL] No results for: {refined_query}")
                return self._generate_fallback_response(message)

            # Step 3–4: Synthesize response
            logger.info("[FAQ_TOOL] Synthesizing FAQ response")
            synthesized = await self._synthesize_faq_response(message, search_results)

            # Step 5: Format final response
            logger.info("[FAQ_TOOL] Formatting response with citations")
            return self._format_faq_response(synthesized, search_results)

        except Exception as e:
            logger.error(f"[FAQ_TOOL] Error in dynamic FAQ process: {e}")
            return self._generate_fallback_response(message)


    async def _refine_faq_query(self, message: str) -> str:
        """Refine user's question into an optimized search query."""
        refinement_prompt = load_prompt("refinement_prompt").format(
            org_name=ORG_NAME, message=message
        )
        response = await self.llm.ainvoke([HumanMessage(content=refinement_prompt)])
        refined_query = response.content.strip()
        logger.info(f"[FAQ_TOOL] Refined query: {refined_query}")
        return refined_query


    async def _synthesize_faq_response(
        self, message: str, search_results: List[Dict[str, Any]]
    ) -> str:
        """Generate a synthesized answer from search results."""
        # Build context (top 5 results)
        results_context = ""
        for i, result in enumerate(search_results[:5]):
            title = result.get("title", "N/A")
            content = result.get("content", "N/A")
            if isinstance(content, str) and len(content) > 500:
                content = content[:500] + "..."
            url = result.get("url", "N/A")
            results_context += f"\nResult {i+1}:\nTitle: {title}\nContent: {content}\nURL: {url}\n"

        # Build synthesis prompt
        synthesis_prompt = load_prompt("synthesis_prompt").format(
            org_name=ORG_NAME, message=message, results_context=results_context
        )

        # LLM synthesis
        response = await asyncio.wait_for(
            self.llm.ainvoke([HumanMessage(content=synthesis_prompt)]),
            timeout=FAQ_LLM_TIMEOUT,
        )

        synthesized_answer = response.content.strip()
        logger.debug(f"[FAQ_TOOL] Synthesized response: {synthesized_answer[:100]}...")
        return synthesized_answer


    def _format_faq_response(
        self, synthesized_answer: str, search_results: List[Dict[str, Any]]
    ) -> str:
        """Append top sources to the synthesized answer."""
        formatted = synthesized_answer
        if search_results:
            formatted += "\n\n**📚 Sources:**"
            for i, result in enumerate(search_results[:3]):
                title = result.get("title", "Source")
                url = result.get("url", "#")
                formatted += f"\n{i+1}. [{title}]({url})"
        return formatted

    def _generate_fallback_response(self, message: str) -> str:
        """Return a friendly fallback message when no data is found."""
        return (
            f"I’d love to help you learn about {ORG_NAME}, but I couldn’t find current information for your question:\n"
            f"“{message}”\n\n"
            "This might be because:\n"
            "- The information isn’t publicly available yet\n"
            "- The search terms need to be more specific\n"
            "- There might be temporary connectivity issues\n\n"
            f"Try asking a more specific question, or visit our official website and documentation for the most up-to-date info about {ORG_NAME}."
        )

async def handle_faq_node(state: AgentState, search_tool: Any, llm: Any) -> dict:
    """
    Legacy compatibility wrapper for backward support.
    Use FAQTool.get_response() directly in new code.
    """
    tool = FAQTool(search_tool, llm)
    return await tool.get_response(state)
