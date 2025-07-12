import logging
import re
from typing import Dict, Any, List
from .search_tool import TavilySearchTool

logger = logging.getLogger(__name__)

class EnhancedFAQTool:
    """Enhanced FAQ handling tool with web search for organizational queries"""

    def __init__(self, search_tool: TavilySearchTool | None = None):
        self.search_tool = search_tool or TavilySearchTool()

        # Static FAQ responses for technical questions
        self.technical_faq_responses = {
            "how do i contribute": (
                "You can contribute by visiting our GitHub repository, checking open issues, "
                "and submitting pull requests. We welcome all types of contributions including "
                "code, documentation, and bug reports."
            ),
            "how do i report a bug": (
                "You can report a bug by opening an issue on our GitHub repository. "
                "Please include detailed information about the bug, steps to reproduce it, "
                "and your environment."
            ),
            "how to get started": (
                "To get started with Devr.AI: 1) Check our documentation, 2) Join our Discord "
                "community, 3) Explore the GitHub repository, 4) Try contributing to open issues."
            ),
            "what is langgraph": (
                "LangGraph is a framework for building stateful, multi-actor applications "
                "with large language models. We use it to create intelligent agent workflows "
                "for our DevRel automation."
            )
        }

        # Patterns that indicate organizational queries
        self.organizational_patterns = [
            r"what.*is.*(devr\.ai|organization|company|this.*project)",
            r"what.*does.*(devr\.ai|organization|company|this.*project).*do",
            r"(about|tell me about).*(devr\.ai|organization|company|this.*project)",
            r"what.*projects.*(do you have|does.*have|are there)",
            r"what.*goals.*(devr\.ai|organization|company)",
            r"what.*mission.*(devr\.ai|organization|company)",
            r"how.*does.*(devr\.ai|organization|company).*work",
            r"what.*platforms.*(devr\.ai|support|integrate)",
            r"who.*maintains.*(devr\.ai|organization|company)",
            r"what.*kind.*projects.*(devr\.ai|organization|company)"
        ]

    def _is_organizational_query(self, question: str) -> bool:
        """Check if the question is about the organization using pattern matching"""
        question_lower = question.lower().strip()

        for pattern in self.organizational_patterns:
            if re.search(pattern, question_lower):
                return True

        # Additional keyword-based detection
        org_keywords = ["devr.ai", "organization", "company", "projects", "mission", "goals", "about us"]
        question_keywords = ["what", "how", "tell me", "explain", "describe"]

        has_org_keyword = any(keyword in question_lower for keyword in org_keywords)
        has_question_keyword = any(keyword in question_lower for keyword in question_keywords)

        return has_org_keyword and has_question_keyword

    def _generate_search_queries(self, question: str) -> List[str]:
        """Generate targeted search queries for organizational information"""
        base_queries = []
        question_lower = question.lower()

        # Project-related queries
        if any(word in question_lower for word in ["project", "projects", "work on", "building"]):
            base_queries.extend([
                "Devr.AI open source projects",
                "Devr.AI GitHub repositories",
                "Devr.AI projects developer relations"
            ])

        # Mission/goals queries
        if any(word in question_lower for word in ["mission", "goal", "purpose", "about"]):
            base_queries.extend([
                "Devr.AI mission developer relations",
                "About Devr.AI organization",
                "Devr.AI goals AI automation"
            ])

        # Platform/integration queries
        if any(word in question_lower for word in ["platform", "platforms", "integrate", "support"]):
            base_queries.extend([
                "Devr.AI supported platforms integrations",
                "Devr.AI Discord Slack GitHub integration",
                "Devr.AI platform compatibility"
            ])

        # General organizational info
        if any(word in question_lower for word in ["what is", "tell me about", "how does", "work"]):
            base_queries.extend([
                "Devr.AI developer relations AI assistant",
                "Devr.AI official website",
                "Devr.AI community automation"
            ])

        # If no specific patterns matched, use generic queries
        if not base_queries:
            base_queries = [
                "Devr.AI developer relations",
                "Devr.AI AI automation",
                "Devr.AI open source"
            ]

        return base_queries

    async def _search_organizational_info(self, question: str) -> Dict[str, Any]:
        """Search for organizational information using web search"""
        search_queries = self._generate_search_queries(question)
        all_results = []

        for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limits
            try:
                results = await self.search_tool.search(query, max_results=3)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Error searching for '{query}': {str(e)}")

        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return {
            "type": "organizational_info",
            "query": question,
            "search_queries": search_queries,
            "results": unique_results[:5],  # Limit to top 5 results
            "source": "web_search"
        }

    def _synthesize_organizational_response(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """Create a synthesized response from search results"""
        if not search_results:
            return self._get_fallback_response(question)

        # Extract relevant information from search results
        response_parts = []
        sources = []

        for result in search_results[:3]:  # Use top 3 results
            title = result.get('title', '')
            content = result.get('content', '')
            url = result.get('url', '')

            if content and len(content) > 50:  # Only use substantial content
                # Take first 200 characters of content
                snippet = content[:200] + "..." if len(content) > 200 else content
                response_parts.append(snippet)
                sources.append({"title": title, "url": url})

        if response_parts:
            synthesized_answer = " ".join(response_parts)
            return synthesized_answer
        else:
            return self._get_fallback_response(question)

    def _get_fallback_response(self, question: str) -> str:
        """Provide a fallback response when search results are insufficient"""
        return ("Devr.AI is an AI-powered Developer Relations assistant that helps open-source communities "
                "by automating engagement, issue tracking, and providing intelligent support to developers. "
                "For the most up-to-date information about our projects and organization, please visit our "
                "official website and GitHub repository.")

    async def get_response(self, question: str) -> Dict[str, Any]:
        """Get FAQ response - either static or dynamic based on query type"""
        question_lower = question.lower().strip()

        # First, check static technical FAQ responses
        for faq_key, response in self.technical_faq_responses.items():
            if self._is_similar_question(question_lower, faq_key):
                return {
                    "type": "static_faq",
                    "response": response,
                    "source": "faq_database",
                    "sources": []
                }

        # Check if this is an organizational query
        if self._is_organizational_query(question):
            logger.info(f"Detected organizational query: {question}")
            search_result = await self._search_organizational_info(question)

            synthesized_response = self._synthesize_organizational_response(
                question, search_result.get("results", [])
            )

            # Format sources for response
            sources = []
            for result in search_result.get("results", [])[:3]:
                if result.get('title') and result.get('url'):
                    sources.append({
                        "title": result.get('title', ''),
                        "url": result.get('url', '')
                    })

            return {
                "type": "organizational_faq",
                "response": synthesized_response,
                "source": "web_search",
                "sources": sources,
                "search_queries": search_result.get("search_queries", [])
            }

        # If no match found, return None to indicate no FAQ response available
        return {
            "type": "no_match",
            "response": None,
            "source": "none",
            "sources": []
        }

    def _is_similar_question(self, question: str, faq_key: str) -> bool:
        """Check if question is similar to FAQ key using simple keyword matching"""
        question_words = set(question.split())
        faq_words = set(faq_key.split())

        common_words = question_words.intersection(faq_words)
        return len(common_words) >= 2  # At least 2 common words
