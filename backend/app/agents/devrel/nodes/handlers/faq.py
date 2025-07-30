import logging
from typing import List

from app.agents.state import AgentState
from app.agents.devrel.tools.search_tool.ddg import DuckDuckGoSearchTool
from langchain_core.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger(__name__)


async def _generate_queries_with_llm(llm: BaseChatModel, question: str) -> List[str]:
    """Use LLM to generate 2–3 refined search queries for a FAQ question."""
    try:
        prompt = (
            "You are an AI assistant. Given the following user question, "
            "generate 2–3 specific search queries that can help answer it accurately from the web. "
            "Only return the queries, one per line, no bullet points.\n\n"
            f"User question: {question}"
        )

        response = await llm.ainvoke([HumanMessage(content=prompt)])
        raw_queries = response.content.strip().split("\n")
        queries = [q.strip() for q in raw_queries if q.strip()]
        return queries or [question]
    except Exception as e:
        logger.warning(
            f"[FAQ Handler] Query generation failed, using fallback. Error: {e}"
        )
        return [question]


async def handle_faq_node_with_llm(state: AgentState, llm: BaseChatModel) -> dict:
    """Handles general FAQ by searching the web with LLM-generated queries."""
    logger.info(f"[FAQ Handler] Handling FAQ for session {state.session_id}")

    # Extract latest user message
    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    if not latest_message:
        logger.warning("[FAQ Handler] No user question found.")
        return {
            "task_result": {
                "type": "faq",
                "response": "Sorry, I couldn't find the question to answer.",
                "source": "web_faq_llm"
            },
            "current_task": "faq_handled"
        }

    # Generate refined queries
    queries = await _generate_queries_with_llm(llm, latest_message)

    # Run web search
    search_tool = DuckDuckGoSearchTool()
    results = []

    for query in queries:
        try:
            result = await search_tool.ainvoke(query)
            results.append(f"Query: {query}\n{result}")
        except Exception as e:
            logger.warning(
                f"[FAQ Handler] Search failed for query: {query} — {e}"
            )

    # Combine and return results
    combined_result = (
        "\n\n".join(results) if results else "Sorry, no results found from the web."
    )

    return {
        "task_result": {
            "type": "faq",
            "response": combined_result,
            "source": "web_faq_llm"
        },
        "current_task": "faq_handled"
    }
