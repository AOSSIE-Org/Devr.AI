import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from .prompts.intent_analysis import GITHUB_INTENT_ANALYSIS_PROMPT
from .tools.search import handle_web_search
# TODO: Implement all tools
from .tools.contributor_recommendation import handle_contributor_recommendation
# from .tools.repository_query import handle_repo_query
# from .tools.issue_creation import handle_issue_creation
# from .tools.documentation_generation import handle_documentation_generation
from .tools.general_github_help import handle_general_github_help
logger = logging.getLogger(__name__)


class GitHubToolkit:
    """
    GitHub Toolkit - Main entry point for GitHub operations

    This class serves as both the intent classifier and execution coordinator.
    It thinks (classifies intent) and acts (delegates to appropriate tools).
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.github_agent_model,
            temperature=0.1,
            google_api_key=settings.gemini_api_key
        )
        self.tools = [
            "web_search",
            "contributor_recommendation",
            "repo_support",
            "issue_creation",
            "documentation_generation",
            "find_good_first_issues",
            "general_github_help"
        ]

    async def classify_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Classify intent and return classification with reasoning.

        Args:
            user_query: The user's request or question

        Returns:
            Dictionary containing classification, reasoning, and confidence
        """
        logger.info(f"Classifying intent for query: {user_query[:100]}")

        try:
            prompt = GITHUB_INTENT_ANALYSIS_PROMPT.format(user_query=user_query)
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])

            import json
            result = json.loads(response.content.strip())

            classification = result.get("classification")
            if classification not in self.tools:
                logger.warning(f"Returned invalid function: {classification}, defaulting to general_github_help")
                classification = "general_github_help"
                result["classification"] = classification

            result["query"] = user_query

            logger.info(f"Classified intent as for query: {user_query} is: {classification}")
            logger.info(f"Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            logger.info(f"Confidence: {result.get('confidence', 'unknown')}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response from LLM: {str(e)}")
            logger.error(f"Raw response: {response.content}")
            return {
                "classification": "general_github_help",
                "reasoning": f"Failed to parse LLM response: {str(e)}",
                "confidence": "low",
                "query": user_query
            }
        except Exception as e:
            logger.error(f"Error in intent classification: {str(e)}")
            return {
                "classification": "general_github_help",
                "reasoning": f"Error occurred during classification: {str(e)}",
                "confidence": "low",
                "query": user_query
            }

    async def execute(self, query: str) -> Dict[str, Any]:
        """
        Main execution method - classifies intent and delegates to appropriate tools
        """
        logger.info(f"Executing GitHub toolkit for query: {query[:100]}")

        try:
            intent_result = await self.classify_intent(query)
            classification = intent_result["classification"]

            logger.info(f"Executing {classification} for query")

            if classification == "contributor_recommendation":
                result = await handle_contributor_recommendation(query)
            elif classification == "repo_support":
                result = {"status": "not_implemented", "message": "Repo support not implemented yet"}
                # result = await handle_repo_query(query)
            elif classification == "issue_creation":
                result = "Not implemented"
                # result = await handle_issue_creation(query)
            elif classification == "documentation_generation":
                result = {"status": "not_implemented", "message": "Documentation generation is not yet implemented"}
                # result = await handle_documentation_generation(query)
            elif classification == "web_search":
                result = await handle_web_search(query)
            else:
                result = await handle_general_github_help(query, self.llm)

            result["intent_analysis"] = intent_result
            result["type"] = "github_toolkit"

            return result

        except Exception as e:
            logger.error(f"Error in GitHub toolkit execution: {str(e)}")
            return {
                "status": "error",
                "type": "github_toolkit",
                "query": query,
                "error": str(e),
                "message": "Failed to execute GitHub operation"
            }
