import logging
from typing import Dict, Any, List
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Prompt for synthesizing organizational responses
ORGANIZATIONAL_SYNTHESIS_PROMPT = """You are a helpful AI assistant representing Devr.AI. \
Based on the search results below, provide a comprehensive and accurate answer to the \
user's question about our organization.

User Question: "{question}"

Search Results:
{search_results}

Instructions:
1. Synthesize the information from the search results into a coherent, informative response
2. Focus on providing accurate information about Devr.AI
3. Be concise but comprehensive
4. If the search results don't contain enough information, acknowledge this and provide what you can
5. Maintain a professional and friendly tone
6. Do not make up information not present in the search results

Response:"""

async def handle_organizational_faq_node(state: AgentState, enhanced_faq_tool, llm) -> Dict[str, Any]:
    """Handle organizational FAQ requests with web search and LLM synthesis"""
    logger.info(f"Handling organizational FAQ for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    # Get response from enhanced FAQ tool
    faq_response = await enhanced_faq_tool.get_response(latest_message)

    # If it's an organizational query, enhance with LLM synthesis
    if faq_response.get("type") == "organizational_faq":
        search_results = faq_response.get("sources", [])

        if search_results:
            # Format search results for LLM
            formatted_results = _format_search_results_for_llm(search_results)

            # Use LLM to synthesize a better response
            synthesis_prompt = ORGANIZATIONAL_SYNTHESIS_PROMPT.format(
                question=latest_message,
                search_results=formatted_results
            )

            try:
                llm_response = await llm.ainvoke([HumanMessage(content=synthesis_prompt)])
                synthesized_answer = llm_response.content.strip()

                # Update the response with the synthesized answer
                faq_response["response"] = synthesized_answer
                faq_response["synthesis_method"] = "llm_enhanced"

                logger.info(
                    f"Enhanced organizational response with LLM synthesis "
                    f"for session {state.session_id}"
                )
            except Exception as e:
                logger.error(f"Error in LLM synthesis: {str(e)}")
                # Keep the original response if LLM synthesis fails
                faq_response["synthesis_method"] = "basic"

    return {
        "task_result": {
            "type": "organizational_faq",
            "response": faq_response.get("response"),
            "source": faq_response.get("source", "enhanced_faq"),
            "sources": faq_response.get("sources", []),
            "search_queries": faq_response.get("search_queries", []),
            "synthesis_method": faq_response.get("synthesis_method", "none"),
            "query_type": faq_response.get("type", "unknown")
        },
        "current_task": "organizational_faq_handled"
    }

def _format_search_results_for_llm(search_results: List[Dict[str, Any]]) -> str:
    """Format search results for LLM synthesis"""
    if not search_results:
        return "No search results available."

    formatted_parts = []
    for i, result in enumerate(search_results, 1):
        title = result.get('title', 'No title')
        url = result.get('url', 'No URL')
        content = result.get('content', 'No content available')

        formatted_part = f"""
Result {i}:
Title: {title}
URL: {url}
Content: {content[:500]}{"..." if len(content) > 500 else ""}
"""
        formatted_parts.append(formatted_part)

    return "\n".join(formatted_parts)

def create_organizational_response(task_result: Dict[str, Any]) -> str:
    """Create a user-friendly response string from organizational FAQ results"""
    response = task_result.get("response", "")
    sources = task_result.get("sources", [])
    query_type = task_result.get("query_type", "")

    if not response:
        return ("I couldn't find specific information about that. Please try rephrasing your "
                "question or check our official documentation.")

    # Start with the main response
    response_parts = [response]

    # Add sources if available
    if sources:
        response_parts.append("\n\n**Sources:**")
        for i, source in enumerate(sources[:3], 1):
            title = source.get('title', 'Source')
            url = source.get('url', '')
            response_parts.append(f"{i}. [{title}]({url})")

    # Add helpful footer for organizational queries
    if query_type == "organizational_faq":
        response_parts.append(
            "\n\nFor more information, you can also visit our official website or GitHub repository."
        )

    return "\n".join(response_parts)
