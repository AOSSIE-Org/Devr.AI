import logging
from typing import Dict, Any, Literal, TypedDict, List
from functools import partial
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.runnables import Runnable, RunnablePassthrough

from app.agents.state import AgentState
from app.agents.devrel.github.github_toolkit import GitHubToolkit

logger = logging.getLogger(__name__)

class TechnicalSupportInput(TypedDict):
    """Define the input schema for the HIL workflow."""
    messages: List[Dict[str, Any]]

def clarify_context_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Ask the user for initial context.
    """
    logger.info("HIL Workflow: Clarifying Context")
    hil_message = "I can help with that. To start, are you working in a specific repository, like 'AOSSIE-Org/Devr.AI'?"
    
    return {
        "hil_message": hil_message,
        "current_task": "awaiting_context",
        "final_response": hil_message # Set the response for the bot
    }

def propose_action_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    """
    Node 2: Propose a tool to use based on the context.
    """
    logger.info("HIL Workflow: Proposing Action")

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a technical support supervisor. The user has provided the following context.
Your goal is to propose a *single* GitHub tool call to investigate their problem.
The user is working on a technical issue.
The available tool is 'github_toolkit'.
Based on the conversation, decide what file or issue to investigate first.
Return a JSON object with "action" (tool name) and "args" (tool input string).

Example:
{{
  "action": "github_toolkit",
  "args": "What is the content of the file 'database_connector.py' in the 'AOSSIE-Org/Devr.AI' repo?"
}}
"""),
        ("human", "Here is the conversation so far:\n{messages_str}")
    ])
    
    parser = JsonOutputParser()
    
    messages_str = "\n".join(
        [f"{m['role']}: {m['content']}" for m in state.messages if m.get("content")]
    )
    
    chain = prompt | llm | parser
    
    try:
        proposed_action = chain.invoke({"messages_str": messages_str})
        tool_input = proposed_action.get("args", "run an investigation")
        hil_message = f"Okay, based on that, I plan to investigate the following: '{tool_input}'. Does that sound like the right first step?"

        return {
            "hil_message": hil_message,
            "current_task": "awaiting_action_approval",
            "final_response": hil_message,
            "context": {
                **state.context,
                "supervisor_decision": proposed_action
            }
        }
    except Exception as e:
        logger.error(f"HIL Workflow: Error proposing action: {e}", exc_info=True)
        return {
            "hil_message": "I'm having trouble deciding the next step. Can you please rephrase your problem?",
            "current_task": "awaiting_context", 
            "final_response": "I'm having trouble deciding the next step. Can you please rephrase your problem?"
        }

async def execute_action_node(state: AgentState, github_toolkit: GitHubToolkit) -> Dict[str, Any]:
    """
    Node 3: Run the proposed tool. This does NOT pause.
    """
    logger.info("HIL Workflow: Executing Action")
    
    try:
        supervisor_decision = state.context.get("supervisor_decision")
        if not supervisor_decision or supervisor_decision.get("action") != "github_toolkit":
            raise Exception("No valid action was approved by the user.")
            
        tool_input = supervisor_decision.get("args", "No input provided")
        logger.info(f"HIL Workflow: Executing tool with input: {tool_input}")
        agent_executor = github_toolkit.as_executor()
        
        github_chain = (
            RunnablePassthrough()
            | (lambda x: x.get("input"))
            | agent_executor
        )
        
        tool_result_raw = await github_chain.ainvoke({"input": tool_input})
        tool_message = tool_result_raw.get("output", "Tool executed but provided no output.")

        tool_result = {
            "task_result": {
                "type": "github_toolkit",
                "status": "success",
                "message": tool_message
            }
        }

        return {
            "task_result": tool_result["task_result"],
            "current_task": "action_executed"
        }
    except Exception as e:
        logger.error(f"HIL Workflow: Error executing action: {e}", exc_info=True)
        return {
            "task_result": {
                "type": "github_toolkit",
                "status": "error",
                "message": f"Sorry, I ran into an error trying to run that tool: {e}"
            },
            "current_task": "action_executed"
        }

def present_options_node(state: AgentState, llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    """
    Node 4: Present options to the user based on tool results.
    """
    logger.info("HIL Workflow: Presenting Options")
    
    tool_message = state.task_result.get("message", "I found some information, but I'm not sure what to make of it.")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a helpful technical support assistant.
You will be given the result of a tool you just ran.
Summarize this result for the user and ask them what they'd like to do next (e.g., "Which part should we investigate first?" or "Does this information help?").
Keep your response conversational and clear.
"""),
        ("human", "Here is the tool result:\n{tool_result}")
    ])
    
    chain = prompt | llm
    
    try:
        hil_response = chain.invoke({"tool_result": tool_message})
        hil_message = hil_response.content
    except Exception as e:
        logger.error(f"HIL Workflow: Error in present_options_node: {e}", exc_info=True)
        hil_message = f"The tool returned: {tool_message}\nWhat would you like to do next?"

    return {
        "hil_message": hil_message,
        "current_task": "awaiting_option_choice",
        "final_response": hil_message
    }

def wait_for_user_input_node(state: AgentState) -> Dict[str, Any]:
    """
    This node is the destination *after* a pause.
    """
    logger.info(f"HIL Workflow: Resuming from pause. Messages: {len(state.messages)}")
    return {
        "hil_message": None,
        "waiting_for_human_input": False
    }

def smart_entry_node(state: AgentState) -> Dict[str, Any]:
    """
    Smart entry point that detects if we're resuming or starting fresh.
    """
    is_resuming = (
        state.current_task and 
        state.current_task != "None" and
        len(state.messages) > 1
    )
    
    if is_resuming:
        logger.info(f"HIL Workflow: Resuming - task={state.current_task}, messages={len(state.messages)}")
    else:
        logger.info("HIL Workflow: Starting fresh - going to clarify_context")
    
    return {}

def pause_marker_node(state: AgentState) -> Dict[str, Any]:
    """
    A no-op node used purely as an interrupt target.
    """
    logger.info("HIL Workflow: Pause marker reached")
    return {}

def resume_router(state: AgentState) -> Literal["propose_action", "execute_action", "propose_action_loop", "__end__"]:
    """
    This router directs the flow *after* the user provides input.
    """
    task = state.current_task
    logger.info(f"HIL Workflow: Resuming. Last task was: {task}")
    
    if task == "awaiting_context":
        return "propose_action"
    if task == "awaiting_action_approval":
        return "execute_action"
    if task == "awaiting_option_choice":
        return "propose_action_loop"
    
    return "__end__"

def create_technical_support_workflow(
    llm: ChatGoogleGenerativeAI, 
    github_toolkit: GitHubToolkit, 
    checkpointer: BaseCheckpointSaver
) -> StateGraph:
    """
    Factory function to create the HIL workflow graph.
    """
    
    workflow = StateGraph(AgentState, TechnicalSupportInput)

    workflow.add_node("smart_entry", smart_entry_node)
    workflow.add_node("clarify_context", clarify_context_node)
    workflow.add_node("propose_action", partial(propose_action_node, llm=llm))
    workflow.add_node("execute_action", partial(execute_action_node, github_toolkit=github_toolkit))
    workflow.add_node("present_options", partial(present_options_node, llm=llm))
    workflow.add_node("pause_here", pause_marker_node)
    workflow.add_node("wait_for_user", wait_for_user_input_node)

    workflow.set_entry_point("smart_entry")
    
    def smart_entry_router(state: AgentState) -> Literal["wait_for_user", "clarify_context"]:
        """Route based on whether we're resuming or starting fresh"""
        try:
            is_resuming = (
                state.current_task and 
                state.current_task != "None" and
                len(state.messages) > 1
            )
            return "wait_for_user" if is_resuming else "clarify_context"
        except Exception:
            return "clarify_context"
    
    workflow.add_conditional_edges(
        "smart_entry",
        smart_entry_router,
        {
            "wait_for_user": "wait_for_user",
            "clarify_context": "clarify_context"
        }
    )

    workflow.add_edge("clarify_context", "pause_here")
    workflow.add_edge("pause_here", "wait_for_user")
    
    workflow.add_conditional_edges(
        "wait_for_user",
        lambda state: resume_router(state),
        {
            "propose_action": "propose_action",
            "execute_action": "execute_action",
            "propose_action_loop": "propose_action",
            "__end__": END
        }
    )
    
    workflow.add_edge("propose_action", "pause_here")
    workflow.add_edge("execute_action", "present_options")
    workflow.add_edge("present_options", "pause_here")

    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["pause_here"]
    )