import logging
from typing import Optional
from langsmith import traceable

logger = logging.getLogger(__name__)

class FAQTool:
    """FAQ handling tool"""

    # TODO: Add FAQ responses from a database to refer organization's FAQ and Repo's FAQ

    def __init__(self):
        self.faq_responses = {
            "what is devr.ai": "Devr.AI is an AI-powered Developer Relations assistant that helps open-source communities by automating engagement, issue tracking, and providing intelligent support to developers.",
            "how do i contribute": "You can contribute by visiting our GitHub repository, checking open issues, and submitting pull requests. We welcome all types of contributions including code, documentation, and bug reports.",
            "what platforms does devr.ai support": "Devr.AI integrates with Discord, Slack, GitHub, and can be extended to other platforms. We use these integrations to provide seamless developer support across multiple channels.",
            "who maintains devr.ai": "Devr.AI is maintained by an open-source community of developers passionate about improving developer relations and community engagement.",
            "how do i report a bug": "You can report a bug by opening an issue on our GitHub repository. Please include detailed information about the bug, steps to reproduce it, and your environment.",
            "how to get started": "To get started with Devr.AI: 1) Check our documentation, 2) Join our Discord community, 3) Explore the GitHub repository, 4) Try contributing to open issues.",
            "what is langgraph": "LangGraph is a framework for building stateful, multi-actor applications with large language models. We use it to create intelligent agent workflows for our DevRel automation."
        }

    @traceable(name="faq_tool_get_response", run_type="tool")
    async def get_response(self, question: str) -> Optional[str]:
        """Get FAQ response for a question"""
        question_lower = question.lower().strip()

        # Direct match
        if question_lower in self.faq_responses:
            return self.faq_responses[question_lower]

        # Fuzzy matching
        for faq_key, response in self.faq_responses.items():
            if self._is_similar_question(question_lower, faq_key):
                return response

        return None

    @traceable(name="faq_similarity_check", run_type="tool")
    def _is_similar_question(self, question: str, faq_key: str) -> bool:
        """Check if question is similar to FAQ key"""
        # Simple keyword matching - in production, use better similarity or probably cosine similarity
        question_words = set(question.split())
        faq_words = set(faq_key.split())

        common_words = question_words.intersection(faq_words)
        return len(common_words) >= 2  # At least 2 common words
