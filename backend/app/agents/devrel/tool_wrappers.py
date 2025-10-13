import logging
from typing import Dict, Any
from app.agents.state import AgentState
from .nodes.react_supervisor import add_tool_result
from app.agents.devrel.tools.faq_tool import handle_faq_node
from .nodes.handlers.web_search import handle_web_search_node
from .nodes.handlers.onboarding import handle_onboarding_node

logger = logging.getLogger(__name__)

async def web_search_tool_node(state: AgentState, search_tool, llm) -> Dict[str, Any]:
    """Execute web search tool and add result to ReAct context"""
    logger.info(f"Executing web search tool for session {state.session_id}")
    handler_result = await handle_web_search_node(state, search_tool, llm)
    tool_result = handler_result.get("task_result", {})
    return add_tool_result(state, "web_search", tool_result)

async def faq_handler_tool_node(state: AgentState, search_tool, llm) -> Dict[str, Any]:
    """Execute FAQ handler tool and add result to ReAct context"""
    logger.info(f"Executing FAQ handler tool for session {state.session_id}")

    handler_result = await handle_faq_node(state, search_tool, llm)
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

    latest_message = (
        state.messages[-1].get("content", "")
        if state.messages else
        state.context.get("original_message", "")
    )

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
