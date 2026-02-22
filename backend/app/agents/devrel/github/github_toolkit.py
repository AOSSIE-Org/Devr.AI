from app.services.github.issue_suggestion_service import IssueSuggestionService
import logging
import config
from typing import Dict, Any
from app.core.config import settings

from .tools.search import handle_web_search
from .tools.github_support import handle_github_supp
from .tools.contributor_recommendation import handle_contributor_recommendation
from .tools.general_github_help import handle_general_github_help
from .tools.repo_support import handle_repo_support

logger = logging.getLogger(__name__)

DEFAULT_ORG = config.GITHUB_ORG


def normalize_org(org_from_user: str = None) -> str:
    if org_from_user and org_from_user.strip():
        return org_from_user.strip()
    return DEFAULT_ORG


class GitHubToolkit:
    """
    GitHub Toolkit - Rule-based intent classifier + executor
    (Gemini removed to avoid quota issues)
    """

    def __init__(self):
        self.tools = [
            "web_search",
            "contributor_recommendation",
            "repo_support",
            "github_support",
            "issue_creation",
            "documentation_generation",
            "find_good_first_issues",
            "general_github_help"
        ]

    # --------------------------------------------------
    # RULE-BASED CLASSIFIER
    # --------------------------------------------------

    async def classify_intent(self, user_query: str) -> Dict[str, Any]:

        query_lower = user_query.lower()

        if "beginner" in query_lower or "good first issue" in query_lower:
            classification = "find_good_first_issues"

        elif "contributor" in query_lower:
            classification = "contributor_recommendation"

        elif "repo" in query_lower:
            classification = "repo_support"

        elif "github support" in query_lower:
            classification = "github_support"

        elif "search" in query_lower:
            classification = "web_search"

        else:
            classification = "general_github_help"

        logger.info(f"Rule-based classification: {user_query} -> {classification}")

        return {
            "classification": classification,
            "reasoning": "Rule-based classification",
            "confidence": "high",
            "query": user_query
        }

    # --------------------------------------------------
    # EXECUTION
    # --------------------------------------------------

    async def execute(self, query: str) -> Dict[str, Any]:
        logger.info(f"Executing GitHub toolkit for query: {query[:100]}")

        try:
            intent_result = await self.classify_intent(query)
            classification = intent_result["classification"]

            logger.info(f"Executing action: {classification}")

            # -----------------------------------------
            # EXISTING HANDLERS
            # -----------------------------------------

            if classification == "contributor_recommendation":
                result = await handle_contributor_recommendation(query)

            elif classification == "github_support":
                org = normalize_org()
                result = await handle_github_supp(query, org=org)
                result["org_used"] = org

            elif classification == "repo_support":
                result = await handle_repo_support(query)

            elif classification == "issue_creation":
                result = {
                    "message": "Issue creation not implemented yet"
                }

            elif classification == "documentation_generation":
                result = {
                    "message": "Documentation generation not implemented yet"
                }

            # -----------------------------------------
            # BEGINNER ISSUE SEARCH
            # -----------------------------------------

            elif classification == "find_good_first_issues":

                service = IssueSuggestionService(settings.github_token_resolved)

                issues = await service.fetch_beginner_issues(
                    language="python",
                    limit=10
                )

                if not issues:
                    result = {
                        "status": "success",
                        "message": "No beginner issues found globally right now.",
                        "issues": []
                    }
                else:
                    formatted = "\n\n".join(
                        f"🔹 [{i['repo']}] #{i['number']} - {i['title']}\n{i['url']}"
                        for i in issues
                    )

                    result = {
                        "status": "success",
                        "message": f"Here are beginner-friendly issues across GitHub:\n\n{formatted}",
                        "issues": issues
                    }

            elif classification == "web_search":
                result = await handle_web_search(query)

            # -----------------------------------------
            # DEFAULT FALLBACK
            # -----------------------------------------

            else:
                result = await handle_general_github_help(query, None)

            result["intent_analysis"] = intent_result
            result["type"] = "github_toolkit"

            return result

        except Exception as e:
            logger.error(f"GitHub toolkit execution error: {str(e)}")
            return {
                "status": "error",
                "type": "github_toolkit",
                "query": query,
                "error": str(e),
                "message": "Failed to execute GitHub operation"
            }