import logging
from typing import Dict, Any
from functools import partial
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from ..shared.base_agent import BaseAgent, AgentState
from ..shared.classification_router import MessageCategory
from .tools.search_tool import TavilySearchTool
from .tools.faq_tool import FAQTool
from app.core.config import settings
from .nodes.classify_intent_node import classify_intent_node
from .nodes.gather_context_node import gather_context_node
from .nodes.handle_faq_node import handle_faq_node
from .nodes.handle_web_search_node import handle_web_search_node
from .nodes.handle_technical_support_node import handle_technical_support_node
from .nodes.handle_onboarding_node import handle_onboarding_node
from .nodes.generate_response_node import generate_response_node

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
        self.search_tool = TavilySearchTool()
        self.faq_tool = FAQTool()
        super().__init__("DevRelAgent", self.config)

    def _build_graph(self):
        """Build the DevRel agent workflow graph"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classify_intent", partial(classify_intent_node, llm=self.llm))
        workflow.add_node("gather_context", gather_context_node)
        workflow.add_node("handle_faq", partial(handle_faq_node, faq_tool=self.faq_tool))
        workflow.add_node("handle_web_search", partial(
            handle_web_search_node, search_tool=self.search_tool, llm=self.llm))
        workflow.add_node("handle_technical_support", handle_technical_support_node)
        workflow.add_node("handle_onboarding", handle_onboarding_node)
        workflow.add_node("generate_response", partial(generate_response_node, llm=self.llm))

        # Add edges
        workflow.add_edge("classify_intent", "gather_context")
        workflow.add_conditional_edges(
            "gather_context",
            self._route_to_handler,
            {
                MessageCategory.FAQ: "handle_faq",
                MessageCategory.WEB_SEARCH: "handle_web_search",
                MessageCategory.ONBOARDING: "handle_onboarding",
                MessageCategory.TECHNICAL_SUPPORT: "handle_technical_support",
                MessageCategory.COMMUNITY_ENGAGEMENT: "handle_technical_support",
                MessageCategory.DOCUMENTATION: "handle_technical_support",
                MessageCategory.BUG_REPORT: "handle_technical_support",
                MessageCategory.FEATURE_REQUEST: "handle_technical_support",
                "default": "handle_technical_support"
            }
        )

        # All handlers lead to response generation
        for node in ["handle_faq", "handle_web_search", "handle_technical_support", "handle_onboarding"]:
            workflow.add_edge(node, "generate_response")

        workflow.add_edge("generate_response", END)

        # Set entry point
        workflow.set_entry_point("classify_intent")

        self.graph = workflow.compile()

    def _route_to_handler(self, state: AgentState) -> str:
        """Route to the appropriate handler based on intent"""
        intent = state.context.get("intent", MessageCategory.TECHNICAL_SUPPORT)
        logger.info(f"Routing based on intent: {intent} for session {state.session_id}")

        # Mapping from MessageCategory enum to string keys used in add_conditional_edges
        route_map = {
            MessageCategory.FAQ: "faq",
            MessageCategory.WEB_SEARCH: "web_search",
            MessageCategory.ONBOARDING: "onboarding",
            MessageCategory.TECHNICAL_SUPPORT: "technical_support",
            MessageCategory.COMMUNITY_ENGAGEMENT: "technical_support",
            MessageCategory.DOCUMENTATION: "technical_support",
            MessageCategory.BUG_REPORT: "technical_support",
            MessageCategory.FEATURE_REQUEST: "technical_support"
        }

        return route_map.get(intent, "technical_support")
