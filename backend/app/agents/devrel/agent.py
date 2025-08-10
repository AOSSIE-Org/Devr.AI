import logging
from typing import Dict, Any
from functools import partial
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from ..base_agent import BaseAgent, AgentState
from .tools.search_tool.ddg import DuckDuckGoSearchTool
from .tools.faq_tool import FAQTool
from .github.github_toolkit import GitHubToolkit
from app.core.config import settings
from .nodes.gather_context import gather_context_node
from .nodes.summarization import check_summarization_needed, summarize_conversation_node, store_summary_to_database
from .nodes.react_supervisor import react_supervisor_node, supervisor_decision_router
from .tool_wrappers import web_search_tool_node, faq_handler_tool_node, onboarding_tool_node, github_toolkit_tool_node
from .nodes.generate_response import generate_response_node

logger = logging.getLogger(__name__)

class DevRelAgent(BaseAgent):
    """DevRel LangGraph Agent for community support and engagement"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.llm = ChatGoogleGenerativeAI(
            model=settings.devrel_agent_model,
            temperature=0.3,
            google_api_key=settings.gemini_api_key
        )
        self.search_tool = DuckDuckGoSearchTool()
        self.faq_tool = FAQTool()
        self.github_toolkit = GitHubToolkit()
        self.checkpointer = InMemorySaver()
        super().__init__("DevRelAgent", self.config)

    def _build_graph(self):
        """Build the DevRel agent workflow graph"""
        workflow = StateGraph(AgentState)

        # Phase 1: Gather Context
        workflow.add_node("gather_context", gather_context_node)

        # Phase 2: ReAct Supervisor - Decide what to do next
        workflow.add_node("react_supervisor", partial(react_supervisor_node, llm=self.llm))
        workflow.add_node("web_search_tool", partial(web_search_tool_node, search_tool=self.search_tool, llm=self.llm))
        workflow.add_node("faq_handler_tool", partial(
            faq_handler_tool_node, search_tool=self.search_tool, llm=self.llm))
        workflow.add_node("onboarding_tool", onboarding_tool_node)
        workflow.add_node("github_toolkit_tool", partial(github_toolkit_tool_node, github_toolkit=self.github_toolkit))

        # Phase 3: Generate Response
        workflow.add_node("generate_response", partial(generate_response_node, llm=self.llm))

        # Phase 4: Summarization
        workflow.add_node("check_summarization", check_summarization_needed)
        workflow.add_node("summarize_conversation", partial(summarize_conversation_node, llm=self.llm))

        # Entry point
        workflow.set_entry_point("gather_context")
        workflow.add_edge("gather_context", "react_supervisor")

        # ReAct supervisor routing
        workflow.add_conditional_edges(
            "react_supervisor",
            supervisor_decision_router,
            {
                "web_search": "web_search_tool",
                "faq_handler": "faq_handler_tool",
                "onboarding": "onboarding_tool",
                "github_toolkit": "github_toolkit_tool",
                "complete": "generate_response"
            }
        )

        # All tools return to supervisor
        for tool in ["web_search_tool", "faq_handler_tool", "onboarding_tool", "github_toolkit_tool"]:
            workflow.add_edge(tool, "react_supervisor")

        workflow.add_edge("generate_response", "check_summarization")

        # Summarization routing
        workflow.add_conditional_edges(
            "check_summarization",
            self._should_summarize,
            {
                "summarize": "summarize_conversation",
                "end": END
            }
        )

        workflow.add_edge("summarize_conversation", END)

        # Compile with checkpointer
        self.graph = workflow.compile(checkpointer=self.checkpointer)

    def _should_summarize(self, state: AgentState) -> str:
        """Determine if conversation should be summarized"""
        if state.summarization_needed:
            logger.info(f"Summarization needed for session {state.session_id}")
            return "summarize"
        return "end"

    async def get_thread_state(self, thread_id: str) -> Dict[str, Any]:
        """Get the current state of a thread"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.graph.get_state(config)
            return state.values if state else {}
        except Exception as e:
            logger.error(f"Error getting thread state: {str(e)}")
            return {}

    async def clear_thread_memory(self, thread_id: str, force_clear: bool = False) -> bool:
        """Clear memory for a specific thread using memory_timeout_reached flag"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = self.graph.get_state(config)

            if state and state.values:
                agent_state = AgentState(**state.values)

                # Check the memory_timeout_reached flag
                if agent_state.memory_timeout_reached or force_clear:
                    if agent_state.memory_timeout_reached:
                        logger.info(f"Thread {thread_id} timeout flag set, storing final summary and clearing memory")
                    else:
                        logger.info(f"Force clearing memory for thread {thread_id}")

                    # Store final summary to database before clearing
                    await store_summary_to_database(agent_state)

                    # Delete the thread from InMemorySaver
                    self.checkpointer.delete_thread(thread_id)
                    logger.info(f"Successfully cleared memory for thread {thread_id}")
                    return True
                else:
                    logger.info(f"Thread {thread_id} has not timed out, memory preserved")
                    return False
            else:
                logger.info(f"No state found for thread {thread_id}, nothing to clear")
                return True

        except Exception as e:
            logger.error(f"Error clearing thread memory: {str(e)}")
            return False
