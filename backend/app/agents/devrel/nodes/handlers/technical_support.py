import logging
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

async def handle_technical_support_node(
    state: AgentState, 
    config: dict,
    hil_workflow
) -> dict:
    logger.info(f"HIL_NODE: Entering for session {state.session_id}")
    
    try:
        parent_thread_id = config.get("configurable", {}).get("thread_id")
        
        if not parent_thread_id:
            logger.error(f"HIL_NODE: CRITICAL - Could not find parent thread_id in config!")
            raise Exception("Parent thread_id not found in config")

        sub_graph_thread_id = f"{parent_thread_id}-hil"
        sub_graph_config = {"configurable": {"thread_id": sub_graph_thread_id}}
        
        logger.info(f"HIL_NODE: Parent thread: {parent_thread_id}")
        logger.info(f"HIL_NODE: Sub-graph thread: {sub_graph_thread_id}")
        
        if not state.messages:
            logger.warning(f"HIL_NODE: Called for {state.session_id} but no messages in state.")
            return {}

        existing_sub_state = hil_workflow.get_state(sub_graph_config)
        is_interrupted = (
            existing_sub_state 
            and existing_sub_state.next 
            and len(existing_sub_state.next) > 0
        )
        
        input_payload = {}
        if is_interrupted:
            logger.info(f"HIL_NODE: Resuming sub-graph for thread {sub_graph_thread_id}")
            input_payload = {
                "messages": [state.messages[-1]]
            }
        else:
            logger.info(f"HIL_NODE: Initializing new sub-graph for thread {sub_graph_thread_id}")
            
            input_payload = state.model_dump()
            
            input_payload["messages"] = [state.messages[-1]]
            
            input_payload["current_task"] = None
            input_payload["hil_message"] = None
            
        
        logger.info(
            f"HIL_NODE: Invoking sub-graph. Resuming: {is_interrupted}. "
            f"Messages: {len(input_payload.get('messages', []))}"
        )
        
        result = await hil_workflow.ainvoke(input_payload, sub_graph_config)

        if result and result.get("hil_message"):
            logger.info(f"HIL_NODE: Sub-graph is PAUSED, waiting for user.")
            return {
                "final_response": result.get("final_response"),
                "hil_message": result.get("hil_message"),
                "current_task": state.current_task 
            }
        else:
            logger.info(f"HIL_NODE: Sub-graph has FINISHED.")
            hil_workflow.checkpointer.delete(sub_graph_config)
            return {
                "final_response": result.get("final_response", "Technical support session complete."),
                "hil_message": None,
                "current_task": "technical_support_complete" 
            }
        
    except Exception as e:
        logger.error(f"HIL_NODE: Error in HIL workflow: {str(e)}", exc_info=True)
        return {
            "errors": state.errors + [f"Technical support error: {str(e)}"],
            "current_task": "technical_support_error"
        }