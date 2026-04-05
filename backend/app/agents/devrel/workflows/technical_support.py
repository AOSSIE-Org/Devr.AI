import logging
import os
from typing import Dict, Any, Literal, TypedDict, List
from functools import partial
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.json import JsonOutputParser
from app.agents.state import AgentState
from app.agents.devrel.github.github_toolkit import GitHubToolkit

logger = logging.getLogger(__name__)

class TechnicalSupportInput(TypedDict):
    messages: List[Dict[str, Any]]

def check_repo_context_node(state: AgentState) -> Dict[str, Any]:
    existing_repo = state.context.get("target_repo")
    logger.info(f"HIL Context Check: target_repo={existing_repo}")

    if existing_repo:
        return {"current_task": "repo_selected"}
    
    last_msg = state.messages[-1].get("content", "").strip()

    safe_words = ["yes", "y", "no", "n", "ok", "okay", "sure", "cancel", "stop"]
    if last_msg.lower() in safe_words:
        msg = "I missed which repository you're referring to. Could you please type the repository name again?"
        return {
            "hil_message": msg,
            "current_task": "awaiting_repo_name",
            "final_response": msg
        }

    if "/" in last_msg and len(last_msg.split()) == 1:
        logger.info(f"HIL: Detected Repo {last_msg}")
        return {
            "context": {**state.context, "target_repo": last_msg},
            "current_task": "indexing_needed",
            "hil_message": f"Indexing {last_msg}..." # Keep HIL active
        }
    
    if len(last_msg.split()) == 1 and len(last_msg) > 2 and "/" not in last_msg:
        default_org = os.getenv("GITHUB_ORG", "AOSSIE-Org")
        full_repo = f"{default_org}/{last_msg}"
        logger.info(f"HIL: Auto-completed Repo {full_repo}")
        return {
            "context": {**state.context, "target_repo": full_repo},
            "current_task": "indexing_needed",
            "hil_message": f"Indexing {full_repo}..." # Keep HIL active
        }

    hil_msg = "To answer code questions, I need to index the repository. Please enter the repository name (e.g., 'Devr.AI' or 'owner/repo')."
    return {
        "hil_message": hil_msg,
        "current_task": "awaiting_repo_name",
        "final_response": hil_msg
    }

async def index_repo_node(state: AgentState, github_toolkit: GitHubToolkit) -> Dict[str, Any]:
    target_repo = state.context.get("target_repo")
    logger.info(f"HIL Workflow: Indexing {target_repo}")
    
    try:
        tool = github_toolkit.get_tool_by_name("falkor_index_tool")
        result = await tool.arun(target_repo)
        
        if "failed" in result.lower() or "error" in result.lower():
             msg = f"Indexing failed: {result}. Please try checking the repo name."
             return {
                 "hil_message": msg,
                 "current_task": "awaiting_repo_name",
                 "final_response": msg
             }

        msg = f"Indexing complete! {result}\nWhat code question can I answer for you?"
        
        return {
            "hil_message": msg,
            "current_task": "awaiting_context",
            "final_response": msg,
            "context": state.context
        }
    except Exception as e:
        return {
            "hil_message": f"Error indexing {target_repo}: {e}",
            "current_task": "awaiting_repo_name"
        }

def format_messages_safely(messages: list) -> str:
    formatted = []
    for m in messages:
        if isinstance(m, dict):
            role = m.get("role", "unknown")
            content = m.get("content", "")
        elif hasattr(m, "content"):
            role = getattr(m, "type", "unknown")
            content = m.content
        else:
            continue
            
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)

def propose_action_node(state: AgentState, llm: ChatOpenAI) -> Dict[str, Any]:
    logger.info("HIL Workflow: Proposing Action")
    
    last_msg = state.messages[-1]
    content = last_msg.content if hasattr(last_msg, 'content') else last_msg.get('content', '')
    last_user_msg = content.lower().strip()
    
    if last_user_msg in ["yes", "y", "ok", "do it"] and state.context.get("supervisor_decision"):
        return {"current_task": "awaiting_action_approval"}

    repo_full = state.context.get("target_repo", "Devr.AI")
    repo_name = repo_full.split("/")[-1]

    history_str = format_messages_safely(state.messages[-6:])
    logger.info(f"HIL Prompt Context: {history_str}")

    json_example = """{
  "action": "falkor_code_graph_tool",
  "args": "explain authentication logic",
  "confirmation_message": "I'll check the auth logic. OK?"
}"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a technical lead for the repository '{repo_full}'.
The user has asked a question. You must query the code graph (FalkorDB) to answer it.

Current State: The repository is INDEXED and ready.
Your Task: Translate the user's latest question into a natural language query for the tool.

Example Output:
{json_example}

Return JSON ONLY.
"""),
        ("human", "Conversation:\n{history_str}")
    ])
    
    parser = JsonOutputParser()
    
    try:
        chain = prompt | llm | parser
        res = chain.invoke({
            "repo_full": repo_full,
            "history_str": history_str,
            "json_example": json_example
        })
        
        hil_msg = res.get("confirmation_message", f"Search code for: '{res.get('args')}'?")
        
        return {
            "hil_message": hil_msg,
            "hil_message": hil_msg,
            "current_task": "action_approved", # AUTO-APPROVE (Skip User input for now)
            "final_response": hil_msg + " (Auto-executing...)",
            "context": {
                **state.context, 
                "supervisor_decision": {**res, "action": "falkor_code_graph_tool", "repo_name": repo_name}
            }
        }
    except Exception as e:
        logger.error(f"PROPOSE ACTION FAILED: {str(e)}", exc_info=True)
        return {
            "hil_message": "I'm having trouble analyzing your request. Should I just scan the repository overview?",
            "current_task": "awaiting_action_approval",
            "context": {**state.context, "supervisor_decision": {"action": "falkor_code_graph_tool", "args": "repository structure overview", "repo_name": repo_name}}
        }

def check_approval_node(state: AgentState) -> Dict[str, Any]:
    logger.info("HIL Workflow: Checking Approval")
    last_msg_obj = state.messages[-1]
    last_msg = ""
    
    if isinstance(last_msg_obj, dict):
        last_msg = last_msg_obj.get("content", "")
    elif hasattr(last_msg_obj, "content"):
        last_msg = last_msg_obj.content
    
    last_msg = last_msg.strip().lower()
    
    if any(x in last_msg for x in ["yes", "y", "ok", "okay", "sure", "do it", "go ahead"]):
        return {"current_task": "action_approved", "context": state.context}
    
    if any(x in last_msg for x in ["no", "stop", "wait", "cancel", "don't"]):
        return {"hil_message": "Cancelled. What should I do?", "current_task": "awaiting_context", "final_response": "Cancelled."}
    
    if len(last_msg.split()) > 3:
        return {"hil_message": None, "current_task": "awaiting_context"}

    return {"current_task": "action_approved", "context": state.context}
async def execute_action_node(state: AgentState, github_toolkit: GitHubToolkit) -> Dict[str, Any]:
    decision = state.context.get("supervisor_decision", {})
    action_name = decision.get("action", "falkor_code_graph_tool")
    if action_name == "technical_support":
        action_name = "falkor_code_graph_tool"
        
    tool = github_toolkit.get_tool_by_name(action_name)
    
    repo_name = decision.get("repo_name", "Devr.AI")
    args = decision.get("args")

    if not args:
        return {"task_result": {"message": "Error: No query arguments found. Please ask your question again."}, "current_task": "action_executed"}

    tool_input = args
    if isinstance(args, str):
        tool_input = {"query": args, "repo_name": repo_name}
    elif isinstance(args, dict):
        tool_input = {**args, "repo_name": repo_name}

    try:
        result = await tool.arun(tool_input)
        return {"task_result": {"message": result}, "current_task": "action_executed"}
    except Exception as e:
        logger.error(f"Tool Execution Failed: {e}")
        return {"task_result": {"message": f"Tool Error: {e}"}, "current_task": "action_executed"}

def present_options_node(state: AgentState, llm: ChatOpenAI) -> Dict[str, Any]:
    msg = state.task_result.get("message", "")
    res = (ChatPromptTemplate.from_messages([("system", "Summarize results concisely:"), ("human", "{res}")]) | llm).invoke({"res": msg})
    
    final_msg = f"{res.content}\n\nWhat else would you like to know about this repository?"
    return {
        "hil_message": final_msg,
        "current_task": "awaiting_context",
        "final_response": final_msg
    }

def wait_for_user_input_node(state: AgentState) -> Dict[str, Any]:
    return {"waiting_for_human_input": False}

def smart_entry_node(state: AgentState) -> Dict[str, Any]: return {}
def pause_marker_node(state: AgentState) -> Dict[str, Any]: return {}

def create_technical_support_workflow(llm, github_toolkit, checkpointer) -> StateGraph:
    workflow = StateGraph(AgentState, TechnicalSupportInput)

    workflow.add_node("smart_entry", smart_entry_node)
    workflow.add_node("check_repo", check_repo_context_node)
    workflow.add_node("index_repo", partial(index_repo_node, github_toolkit=github_toolkit))
    workflow.add_node("propose_action", partial(propose_action_node, llm=llm))
    workflow.add_node("check_approval", check_approval_node)
    workflow.add_node("execute_action", partial(execute_action_node, github_toolkit=github_toolkit))
    workflow.add_node("present_options", partial(present_options_node, llm=llm))
    workflow.add_node("pause_here", pause_marker_node)
    workflow.add_node("wait_for_user", wait_for_user_input_node)

    workflow.set_entry_point("smart_entry")

    # Entry
    workflow.add_conditional_edges("smart_entry", 
        lambda s: "wait_for_user" if (s.current_task and s.current_task != "None" and len(s.messages) > 1) else "check_repo", 
        ["wait_for_user", "check_repo"]
    )

    # Repo Logic
    def repo_router(state):
        if state.current_task == "awaiting_repo_name": return "pause_here"
        if state.current_task == "indexing_needed": return "index_repo"
        return "propose_action"
    workflow.add_conditional_edges("check_repo", repo_router, ["pause_here", "index_repo", "propose_action"])
    
    workflow.add_edge("index_repo", "pause_here")
    workflow.add_edge("propose_action", "pause_here")

    def resume_router(state):
        t = state.current_task
        if t == "awaiting_repo_name": return "check_repo"
        if t == "awaiting_context": return "propose_action"
        if t == "awaiting_action_approval": return "check_approval"
        if t == "action_approved": return "execute_action" # <--- Added for auto-approval
        return END

    workflow.add_conditional_edges("wait_for_user", resume_router, ["check_repo", "propose_action", "check_approval", "execute_action", END])
    
    workflow.add_conditional_edges("check_approval", 
        lambda s: "execute_action" if s.current_task == "action_approved" else "propose_action",
        ["execute_action", "propose_action"]
    )

    workflow.add_edge("execute_action", "present_options")
    workflow.add_edge("present_options", "pause_here")

    return workflow.compile(checkpointer=checkpointer, interrupt_before=["pause_here"])