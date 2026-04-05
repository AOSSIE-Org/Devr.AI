import logging
from typing import Dict, Any
from app.agents.state import AgentState
from langgraph.graph import StateGraph

logger = logging.getLogger(__name__)

async def handle_technical_support_node(
    state: AgentState, 
    config: dict,
    hil_workflow: StateGraph
) -> dict:
    logger.info(f"HIL_NODE: Entering for session {state.session_id}")
    
    try:
        parent_thread_id = config.get("configurable", {}).get("thread_id")
        sub_thread_id = f"{parent_thread_id}-hil"
        sub_config = {"configurable": {"thread_id": sub_thread_id}}
        
        input_payload = {
            "messages": [state.messages[-1]],
            "context": state.context
        }
        
        existing_state = hil_workflow.get_state(sub_config)
        if not existing_state or not existing_state.values:
            logger.info("HIL_NODE: Initializing new sub-graph")
            input_payload = state.model_dump()
            input_payload["messages"] = [state.messages[-1]]

        result = await hil_workflow.ainvoke(input_payload, sub_config)

        updated_context = result.get("context", {})
        current_task = result.get("current_task")
        hil_message = result.get("hil_message")
        final_response = result.get("final_response")

        logger.info(f"HIL_NODE: Sub-graph yielded. Task: {current_task}")
        
        return {
            "context": updated_context, 
            "hil_message": hil_message,
            "current_task": current_task,
            "final_response": final_response
        }

    except Exception as e:
        logger.error(f"HIL_NODE: Error: {e}", exc_info=True)
        return {"current_task": "technical_support_error", "final_response": "An error occurred in technical support."}