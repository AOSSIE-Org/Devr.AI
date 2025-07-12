import logging
from typing import Dict, Any
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

async def handle_faq_node(state: AgentState, faq_tool) -> Dict[str, Any]:
    """Handle FAQ requests with enhanced organizational query support"""
    logger.info(f"Handling FAQ for session {state.session_id}")

    latest_message = ""
    if state.messages:
        latest_message = state.messages[-1].get("content", "")
    elif state.context.get("original_message"):
        latest_message = state.context["original_message"]

    try:
        # Get enhanced response with metadata
        enhanced_response = await faq_tool.get_enhanced_response(latest_message)
        
        # Extract response details
        response_text = enhanced_response.get("response")
        response_type = enhanced_response.get("type", "unknown")
        sources = enhanced_response.get("sources", [])
        search_queries = enhanced_response.get("search_queries", [])
        
        # Log the type of response for monitoring
        logger.info(f"FAQ response type: {response_type} for session {state.session_id}")
        
        if response_text:
            # Successfully got a response
            return {
                "task_result": {
                    "type": response_type,
                    "response": response_text,
                    "source": enhanced_response.get("source", "enhanced_faq"),
                    "sources": sources,
                    "search_queries": search_queries,
                    "has_sources": len(sources) > 0
                },
                "current_task": "faq_handled",
                "tools_used": ["enhanced_faq_tool"]
            }
        else:
            # No response found
            logger.info(f"No FAQ response found for: {latest_message[:100]}")
            return {
                "task_result": {
                    "type": "no_match",
                    "response": None,
                    "source": "enhanced_faq",
                    "sources": [],
                    "search_queries": [],
                    "has_sources": False
                },
                "current_task": "faq_no_match"
            }
            
    except Exception as e:
        logger.error(f"Error in enhanced FAQ handler: {str(e)}")
        
        # Fallback to simple response
        try:
            simple_response = await faq_tool.get_response(latest_message)
            if simple_response:
                return {
                    "task_result": {
                        "type": "fallback_faq",
                        "response": simple_response,
                        "source": "faq_fallback",
                        "sources": [],
                        "search_queries": [],
                        "has_sources": False
                    },
                    "current_task": "faq_handled"
                }
        except Exception as fallback_error:
            logger.error(f"Fallback FAQ also failed: {str(fallback_error)}")
        
        # Return error state
        return {
            "task_result": {
                "type": "error",
                "response": None,
                "source": "error",
                "error": str(e),
                "sources": [],
                "search_queries": [],
                "has_sources": False
            },
            "current_task": "faq_error"
        }
