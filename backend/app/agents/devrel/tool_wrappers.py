import logging
from typing import Dict, Any
from app.agents.state import AgentState
from .nodes.react_supervisor import add_tool_result
from app.agents.devrel.nodes.handlers.faq import handle_faq_node_with_llm
from .nodes.handlers.web_search import handle_web_search_node
from .nodes.handlers.onboarding import handle_onboarding_node
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

async def web_search_tool_node(state: AgentState, search_tool, llm) -> Dict[str, Any]:
    """Execute web search tool and add result to ReAct context"""
    logger.info(f"Executing web search tool for session {state.session_id}")

    handler_result = await handle_web_search_node(state, search_tool, llm)
    tool_result = handler_result.get("task_result", {})
    return add_tool_result(state, "web_search", tool_result)

async def faq_handler_tool_node(state: AgentState, faq_tool) -> Dict[str, Any]:
    """Execute FAQ handler tool and add result to ReAct context"""
    logger.info(f"Executing FAQ handler tool for session {state.session_id}")

    handler_result = await handle_faq_node_with_llm(state, faq_tool)
    tool_result = handler_result.get("task_result", {})
    return add_tool_result(state, "faq_handler", tool_result)

async def onboarding_tool_node(state: AgentState) -> Dict[str, Any]:
    """Execute onboarding tool and add result to ReAct context"""
    logger.info(f"Executing onboarding tool for session {state.session_id}")

    handler_result = await handle_onboarding_node(state)
    tool_result = handler_result.get("task_result", {})
    return add_tool_result(state, "onboarding", tool_result)


async def github_toolkit_tool_node(state: AgentState, github_toolkit) -> Dict[str, Any]:
    """Execute GitHub toolkit tool and add result to ReAct context"""
    logger.info(f"Executing GitHub toolkit tool for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    try:
        github_result = await github_toolkit.execute(latest_message)
        tool_result = github_result
    except Exception as e:
        logger.error(f"Error in GitHub toolkit: {str(e)}")
        tool_result = {
            "type": "github_toolkit",
            "error": str(e),
            "status": "error"
        }

    return add_tool_result(state, "github_toolkit", tool_result)


async def thinking_node_tool_node(state: AgentState, llm) -> Dict[str, Any]:
    """Rephrase user query into a clean and clear question"""
    logger.info(f"Executing Thinking Node for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    # Prompt to rephrase
    prompt = (
        "Rephrase this user query into a clear and formal question "
        "suitable for an FAQ or web search:\n\n"
        f"'{latest_message}'"
    )

    try:
        llm_response = await llm.ainvoke([HumanMessage(content=prompt)])
        clean_question = llm_response.content.strip()
    except Exception as e:
        logger.error(f"Thinking node LLM error: {e}")
        clean_question = latest_message  # fallback

    # Store in state context
    state.context["rephrased_query"] = clean_question

    return add_tool_result(state, "thinking_node", {
        "type": "thinking_node",
        "rephrased_query": clean_question
    })
