import logging
from typing import Dict, Any
from app.agents.shared.state import AgentState
from langchain_core.messages import HumanMessage
from ..prompts.base_prompt import GENERAL_LLM_RESPONSE_PROMPT
from langsmith import traceable

logger = logging.getLogger(__name__)

@traceable(name="create_search_response", run_type="tool")
async def _create_search_response(task_result: Dict[str, Any]) -> str:
    """Create a response string from search results."""
    query = task_result.get("query")
    results = task_result.get("results", [])
    if not results:
        return f"I couldn't find any information for '{query}'. You might want to try rephrasing your search."

    response_parts = [f"Here's what I found for '{query}':"]
    for i, result in enumerate(results[:3]):
        title = result.get('title', 'N/A')
        snippet = result.get('snippet', 'N/A')
        url = result.get('url', '#')
        result_line = f"{i+1}. {title}: {snippet}"
        response_parts.append(result_line)
        response_parts.append(f"   (Source: {url})")
    response_parts.append("You can ask me to search again with a different query if these aren't helpful.")
    return "\n".join(response_parts)

@traceable(name="create_llm_response", run_type="tool")
async def _create_llm_response(state: AgentState, task_result: Dict[str, Any], llm) -> str:
    """Generate a response using the LLM based on the current state and task result."""
    logger.info(f"Creating LLM response for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    conversation_history_str = "\n".join([
        f"{msg.get('type', 'unknown')}: {msg.get('content', '')}"
        for msg in state.conversation_history[-5:]
    ])
    current_context_str = str(state.context)
    task_type_str = str(task_result.get("type", "N/A"))
    task_details_str = str(task_result)

    try:
        prompt = GENERAL_LLM_RESPONSE_PROMPT.format(
            latest_message=latest_message,
            conversation_history=conversation_history_str,
            current_context=current_context_str,
            task_type=task_type_str,
            task_details=task_details_str
        )
    except KeyError as e:
        logger.error(f"Missing key in GENERAL_LLM_RESPONSE_PROMPT: {e}")
        return "Error: Response template formatting error."

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content.strip()

@traceable(name="generate_response_node", run_type="tool")
async def generate_response_node(state: AgentState, llm) -> AgentState:
    """Generate final response to user"""
    logger.info(f"Generating response for session {state.session_id}")
    task_result = state.task_result or {}

    if task_result.get("type") == "faq":
        state.final_response = task_result.get("response", "I don't have a specific answer for that question.")
    elif task_result.get("type") == "web_search":
        response = await _create_search_response(task_result)
        state.final_response = response
    else:
        # Pass the llm instance to _create_llm_response
        response = await _create_llm_response(state, task_result, llm)
        state.final_response = response

    state.current_task = "response_generated"
    return state
