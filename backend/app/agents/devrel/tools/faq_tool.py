import logging
from typing import Optional, Dict, Any
from .enhanced_faq_tool import EnhancedFAQTool
from .search_tool import TavilySearchTool

logger = logging.getLogger(__name__)

class FAQTool:
    """FAQ handling tool with enhanced organizational query support"""

    def __init__(self, search_tool: TavilySearchTool | None = None):
        """Initialize FAQ tool with enhanced functionality"""
        self.enhanced_faq_tool = EnhancedFAQTool(search_tool)

        # Legacy FAQ responses for backward compatibility
        self.legacy_faq_responses = {
            "what is devr.ai": (
                "Devr.AI is an AI-powered Developer Relations assistant that helps open-source "
                "communities by automating engagement, issue tracking, and providing intelligent "
                "support to developers."
            ),
            "what platforms does devr.ai support": (
                "Devr.AI integrates with Discord, Slack, GitHub, and can be extended to other "
                "platforms. We use these integrations to provide seamless developer support "
                "across multiple channels."
            ),
            "who maintains devr.ai": (
                "Devr.AI is maintained by an open-source community of developers passionate "
                "about improving developer relations and community engagement."
            )
        }

    async def get_response(self, question: str) -> Optional[str]:
        """Get FAQ response for a question - enhanced with web search for organizational queries"""
        try:
            # Use the enhanced FAQ tool for better responses
            enhanced_response = await self.enhanced_faq_tool.get_response(question)

            if enhanced_response and enhanced_response.get("response"):
                return enhanced_response.get("response")

            # Fallback to legacy responses for backward compatibility
            question_lower = question.lower().strip()

            # Direct match
            if question_lower in self.legacy_faq_responses:
                return self.legacy_faq_responses[question_lower]

            # Fuzzy matching
            for faq_key, response in self.legacy_faq_responses.items():
                if self._is_similar_question(question_lower, faq_key):
                    return response

            return None

        except Exception as e:
            logger.error(f"Error in FAQ tool: {str(e)}")
            return None

    def _is_similar_question(self, question: str, faq_key: str) -> bool:
        """Check if question is similar to FAQ key"""
        question_words = set(question.split())
        faq_words = set(faq_key.split())

        common_words = question_words.intersection(faq_words)
        return len(common_words) >= 2  # At least 2 common words

    async def get_enhanced_response(self, question: str) -> Dict[str, Any]:
        """Get enhanced FAQ response with metadata for advanced usage"""
        return await self.enhanced_faq_tool.get_response(question)
