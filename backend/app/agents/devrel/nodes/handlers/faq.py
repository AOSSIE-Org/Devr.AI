import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from app.agents.state import AgentState

# Load environment variables from .env file
load_dotenv()

# Configure logger for this module
logger = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.INFO,
#     format="[%(asctime)s] %(levelname)s %(name)s - %(message)s",


# Read org and official handles from env with fallbacks
ORG_NAME = os.getenv("ORG_NAME", "Devr.AI")
# Prefer ORG_* variables from env; fall back to OFFICIAL_HANDLE_*; then to sensible defaults
_org_website = os.getenv("ORG_WEBSITE") or os.getenv("OFFICIAL_HANDLE_1") or "https://aossie.org"
_org_github = os.getenv("ORG_GITHUB") or os.getenv("OFFICIAL_HANDLE_2") or "https://github.com/AOSSIE-Org"
_org_twitter = os.getenv("ORG_TWITTER") or os.getenv("OFFICIAL_HANDLE_3") or "https://twitter.com/aossie_org"

OFFICIAL_HANDLES = [_org_website, _org_github, _org_twitter]


async def handle_faq_node(state: AgentState, search_tool: Any, llm: Any) -> dict:
    """
    Handle FAQ requests dynamically using web search and AI synthesis.
    Pass official handles to search tool if it supports site-restricted queries.
    """
    logger.info(f"[FAQ_HANDLER] Handling dynamic FAQ for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    # Early exit if no message
    if not latest_message:
        logger.warning("[FAQ_HANDLER] Empty latest user message; returning fallback")
        return {
            "task_result": {
                "type": "faq",
                "response": _generate_fallback_response(latest_message, ORG_NAME),
                "source": "dynamic_web_search"
            },
            "current_task": "faq_handled"
        }

    # Append site restrictions to the query if search tool supports it
    try:
        from urllib.parse import urlparse
        domains = []
        for u in OFFICIAL_HANDLES:
            try:
                parsed = urlparse(u)
                domain = parsed.netloc or parsed.path  # handles bare domains
                if domain:
                    domains.append(domain)
            except Exception:
                continue
        site_filters = " OR ".join([f"site:{d}" for d in domains])
    except Exception:
        site_filters = ""
    logger.info(f"[FAQ_HANDLER] Applying site filters for search: {site_filters or '(none)'}")

    faq_response = await _dynamic_faq_process(
        latest_message,
        search_tool,
        llm,
        org_name=ORG_NAME,
        site_filters=site_filters,
    )

    return {
        "task_result": {
            "type": "faq",
            "response": faq_response,
            "source": "dynamic_web_search"
        },
        "current_task": "faq_handled"
    }


async def _dynamic_faq_process(
    message: str,
    search_tool: Any,
    llm: Any,
    org_name: str = ORG_NAME,
    site_filters: str = "",
) -> str:
    """
    Dynamic FAQ handler implementing:
    1. Intent Detection & Query Refinement
    2. Web Search (with site restrictions)
    3. AI-Powered Synthesis
    4. Generate Final Response
    5. Format with Sources
    """
    try:
        # Step 1: Intent Detection & Query Refinement
        logger.info(f"[FAQ_HANDLER] Step 1: Refining FAQ query for org '{org_name}'")
        refined_query = await _refine_faq_query(message, llm, org_name)

        # Append site filters for restricting to official handles
        if site_filters:
            refined_query = f"({refined_query}) AND ({site_filters})"
        logger.info(f"[FAQ_HANDLER] Refined and filtered query: {refined_query}")

        # Step 2: Dynamic Web Search
        logger.info(f"[FAQ_HANDLER] Step 2: Searching for: {refined_query}")
        try:
            search_results = await search_tool.search(refined_query)
        except Exception as search_err:
            logger.error(f"[FAQ_HANDLER] Search tool error: {search_err}")
            return _generate_fallback_response(message, org_name)

        if not search_results:
            logger.warning(f"[FAQ_HANDLER] No results found for query: {refined_query}")
            return _generate_fallback_response(message, org_name)

        # Step 3 & 4: AI-Powered Synthesis & Response Generation
        logger.info("[FAQ_HANDLER] Step 3-4: Synthesizing search results into FAQ response")
        synthesized_response = await _synthesize_faq_response(message, search_results, llm, org_name)

        # Step 5: Format Final Response with Sources
        logger.info("[FAQ_HANDLER] Step 5: Formatting final response with sources")
        final_response = _format_faq_response(synthesized_response, search_results)

        return final_response

    except Exception as e:
        logger.error(f"[FAQ_HANDLER] Error in dynamic FAQ process: {e}")
        return _generate_fallback_response(message, org_name)


async def _refine_faq_query(message: str, llm: Any, org_name: str) -> str:
    """
    Step 1: Refine user query for organization-specific FAQ search.
    """
    refinement_prompt = f"""
You are helping someone find information about {org_name}. 
Transform their question into an effective search query that will find official information about the organization.

User Question: "{message}"

Create a search query that focuses on:
- Official {org_name} information
- The organization's website, blog, or documentation
- Adding terms like "about", "mission", "projects" if relevant

Return only the refined search query, nothing else.

Examples:
- "What does this org do?" → "{org_name} about mission what we do"
- "How do you work?" → "{org_name} how it works process methodology"
- "What projects do you have?" → "{org_name} projects portfolio what we build"
"""
    response = await llm.ainvoke([HumanMessage(content=refinement_prompt)])
    refined_query = response.content.strip()
    logger.info(f"[FAQ_HANDLER] Refined query: {refined_query}")
    return refined_query


async def _synthesize_faq_response(
    message: str,
    search_results: List[Dict[str, Any]],
    llm: Any,
    org_name: str
) -> str:
    """
    Step 3-4: Use LLM to synthesize search results into a comprehensive FAQ answer.
    """
    results_context = ""
    for i, result in enumerate(search_results[:5]):  # Limit to top 5 results
        title = result.get('title', 'N/A')
        content = result.get('content', 'N/A')
        url = result.get('url', 'N/A')
        results_context += f"\nResult {i+1}:\nTitle: {title}\nContent: {content}\nURL: {url}\n"

    synthesis_prompt = f"""
You are an AI assistant representing {org_name}. A user asked: "{message}"

Based on the following search results from official sources, provide a comprehensive, helpful answer about {org_name}.

Search Results:
{results_context}

Instructions:
1. Answer the user's question directly and conversationally
2. Focus on the most relevant and recent information
3. Be informative but concise (2-3 paragraphs max)
4. If the search results don't fully answer the question, acknowledge what you found
5. Sound helpful and knowledgeable about {org_name}
6. Don't mention "search results" in your response - speak as if you know about the organization

Your response:
"""

    response = await llm.ainvoke([HumanMessage(content=synthesis_prompt)])
    synthesized_answer = response.content.strip()
    logger.info(f"[FAQ_HANDLER] Synthesized FAQ response: {synthesized_answer[:100]}...")
    return synthesized_answer


def _format_faq_response(synthesized_answer: str, search_results: List[Dict[str, Any]]) -> str:
    """
    Step 5: Format the final response with sources.
    """
    formatted_response = synthesized_answer

    if search_results:
        formatted_response += "\n\n**📚 Sources:**"
        for i, result in enumerate(search_results[:3]):  # Show top 3 sources
            title = result.get('title', 'Source')
            url = result.get('url', '#')
            formatted_response += f"\n{i+1}. [{title}]({url})"

    return formatted_response


def _generate_fallback_response(message: str, org_name: str) -> str:
    """
    Generate a helpful fallback when search fails.
    """
    return (
        f"I'd be happy to help you learn about {org_name}, but I couldn't find current information to answer your question: \"{message}\"\n\n"
        "This might be because:\n"
        "- The information isn't publicly available yet\n"
        "- The search terms need to be more specific\n"
        "- There might be connectivity issues\n\n"
        "Try asking a more specific question, or check out our official website and documentation for the most up-to-date information about "
        f"{org_name}."
    )


# Example usage for testing
if __name__ == "__main__":
    import asyncio
    from unittest.mock import AsyncMock

    class MockState:
        session_id = "test_session"
        messages = [{"content": "What projects does your organization have?"}]
        context = {}

    async def test_faq_handler():
        mock_state = MockState()
        mock_search_tool = AsyncMock()
        mock_search_tool.search.return_value = [
            {"title": "Project A", "content": "Details about Project A.", "url": "https://aossie.org/projects/a"},
            {"title": "Project B", "content": "Details about Project B.", "url": "https://aossie.org/projects/b"},
        ]
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = AsyncMock(content="We have Project A and Project B focusing on AI and Web.")

        response = await handle_faq_node(mock_state, mock_search_tool, mock_llm)
        print("FAQ Handler response:")
        print(response)

    asyncio.run(test_faq_handler())
