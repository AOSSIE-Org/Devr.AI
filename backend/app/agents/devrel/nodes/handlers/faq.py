import logging
from typing import List, Dict
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

async def handle_faq_node(state: AgentState, search_tool, llm) -> dict:
    """Handle FAQ requests dynamically using web search and AI synthesis"""
    logger.info(f"Handling dynamic FAQ for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    # Dynamic FAQ processing (replaces static faq_tool.get_response)
    faq_response = await _dynamic_faq_process(latest_message, search_tool, llm, org_name="Devr.AI")

    return {
        "task_result": {
            "type": "faq",
            "response": faq_response,
            "source": "dynamic_web_search"  # Updated source
        },
        "current_task": "faq_handled"
    }

async def _dynamic_faq_process(message: str, search_tool, llm, org_name: str = "Devr.AI") -> str:
    """
    Dynamic FAQ handler that implements the 5-step process:
    1. Intent Detection & Query Refinement
    2. Web Search (DuckDuckGo)
    3. AI-Powered Synthesis
    4. Generate Final Response
    5. Format with Sources
    """

    try:
        # Step 1: Intent Detection & Query Refinement
        logger.info(f"Step 1: Refining FAQ query for org '{org_name}'")
        refined_query = await _refine_faq_query(message, llm, org_name)

        # Step 2: Dynamic Web Search
        logger.info(f"Step 2: Searching for: {refined_query}")
        search_results = await search_tool.search(refined_query)

        if not search_results:
            return _generate_fallback_response(message, org_name)

        # Step 3 & 4: AI-Powered Synthesis & Response Generation
        logger.info("Step 3-4: Synthesizing search results into FAQ response")
        synthesized_response = await _synthesize_faq_response(
            message, search_results, llm, org_name
        )

        # Step 5: Format Final Response with Sources
        logger.info("Step 5: Formatting final response with sources")
        final_response = _format_faq_response(synthesized_response, search_results)

        return final_response

    except Exception as e:
        logger.error(f"Error in dynamic FAQ process: {e}")
        return _generate_fallback_response(message, org_name)

async def _refine_faq_query(message: str, llm, org_name: str) -> str:
    """Step 1: Refine user query for organization-specific FAQ search"""

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
    logger.info(f"Refined query: {refined_query}")
    return refined_query

async def _synthesize_faq_response(message: str, search_results: List[Dict], llm, org_name: str) -> str:
    """Step 3-4: Use LLM to synthesize search results into a comprehensive FAQ answer"""

    # Prepare search results context
    results_context = ""
    for i, result in enumerate(search_results[:5]):  # Top 5 results
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
    logger.info(f"Synthesized FAQ response: {synthesized_answer[:100]}...")
    return synthesized_answer

def _format_faq_response(synthesized_answer: str, search_results: List[Dict]) -> str:
    """Step 5: Format the final response with sources"""

    # Start with the synthesized answer
    formatted_response = synthesized_answer

    # Add sources section
    if search_results:
        formatted_response += "\n\n**📚 Sources:**"
        for i, result in enumerate(search_results[:3]):  # Top 3 sources
            title = result.get('title', 'Source')
            url = result.get('url', '#')
            formatted_response += f"\n{i+1}. [{title}]({url})"

    return formatted_response

def _generate_fallback_response(message: str, org_name: str) -> str:
    """Generate a helpful fallback when search fails"""
    return f"""I'd be happy to help you learn about {org_name}, but I couldn't find current information to answer your question: "{message}"

This might be because:
- The information isn't publicly available yet
- The search terms need to be more specific
- There might be connectivity issues


Try asking a more specific question, or check out our official website and documentation for the most up-to-date information about {org_name}."""
