import logging
import re
from typing import Any, Dict
from urllib.parse import urlparse
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.database.weaviate.operations import search_contributors
from app.services.github.issue_processor import GitHubIssueProcessor
from app.services.embedding_service.service import EmbeddingService
from ..prompts.contributor_recommendation.query_alignment import QUERY_ALIGNMENT_PROMPT

logger = logging.getLogger(__name__)

class ContributorRecommendationWorkflow:
    """
    Contributor recommendation with proper query alignment for hybrid search.
    """

    def __init__(self):
        self.query_alignment_llm = ChatGoogleGenerativeAI(
            model=settings.github_agent_model,
            temperature=0.1,
            google_api_key=settings.gemini_api_key
        )
        self.embedding_service = EmbeddingService()

    async def _align_user_request(self, query: str) -> Dict[str, Any]:
        """
        Align user request into optimized format for hybrid search.
        Extract clean technical query + keywords that match contributor profiles.
        """
        logger.info("Aligning user request for hybrid search optimization")

        url_match = re.search(r'https?://github\.com/[\w-]+/[\w.-]+/issues/\d+', query)

        if url_match:
            issue_content = await self._fetch_github_issue_content(url_match.group(0))
            full_query = f"{query}\n\nIssue content: {issue_content}"
        else:
            full_query = query

        prompt = QUERY_ALIGNMENT_PROMPT.format(query=full_query)
        response = await self.query_alignment_llm.ainvoke([HumanMessage(content=prompt)])

        try:
            import json
            print(response)
            result = json.loads(response.content.strip())
            logger.info(f"Query aligned: '{result.get('aligned_query')}' with keywords: {result.get('keywords')}")
            return result
        except json.JSONDecodeError:
            logger.warning("Failed to parse alignment result, using fallback")
            return {
                "query_type": "general",
                "aligned_query": query,
                "keywords": [],
                "technical_domain": "other"
            }

    async def _fetch_github_issue_content(self, github_url: str) -> str:
        """Fetch GitHub issue content."""
        try:
            parsed_url = urlparse(github_url)
            path_parts = parsed_url.path.strip('/').split('/')

            if len(path_parts) >= 4 and path_parts[2] == "issues":
                owner, repo, issue_number = path_parts[0], path_parts[1], int(path_parts[3])
                processor = GitHubIssueProcessor(owner, repo, issue_number)

                content = await processor.fetch_issue_content()
                return content
            else:
                raise ValueError("Invalid GitHub issue URL")

        except Exception as e:
            logger.error(f"GitHub issue fetching failed: {e}")
            raise

async def handle_contributor_recommendation(query: str) -> Dict[str, Any]:
    """
    Main entry point with unified query processing.
    """
    logger.info(f"Processing contributor recommendation: {query[:100]}...")

    try:
        workflow = ContributorRecommendationWorkflow()

        alignment_result = await workflow._align_user_request(query)
        search_text = alignment_result.get("aligned_query", query)

        logger.info("Generating embedding for semantic search")
        enhanced_search_text = f"Looking for contributor with expertise in: {search_text}"
        query_embedding = await workflow.embedding_service.get_embedding(enhanced_search_text)
        logger.info(f"Generated embedding with dimension: {len(query_embedding)}")

        logger.info("Performing hybrid search (semantic + keyword matching)")

        results = await search_contributors(
            query_embedding=query_embedding,
            keywords=alignment_result.get("keywords", []),
            limit=5,
            vector_weight=0.7,  # Semantic similarity
            bm25_weight=0.3     # Keyword matching
        )

        logger.info(f"Search complete: Found {len(results)} potential contributors")

        if not results:
            logger.info("No contributors found matching the search criteria")
            return {
                "status": "success",
                "recommendations": [],
                "message": "No suitable contributors found",
                "search_query": search_text,
                "keywords_used": alignment_result.get("keywords", []),
                "technical_domain": alignment_result.get("technical_domain", "other")
            }

        logger.info("Formatting recommendations with scores")
        recommendations = []
        for contributor in results:
            languages = contributor.get('languages', [])
            topics = contributor.get('topics', [])
            hybrid_score = contributor.get('hybrid_score', 0)
            vector_score = contributor.get('vector_score', 0)
            bm25_score = contributor.get('bm25_score', 0)

            reason_parts = []
            if languages:
                reason_parts.append(f"Expert in {', '.join(languages)}")
            if topics:
                reason_parts.append(f"Active in {', '.join(topics)}")

            username = contributor.get("github_username")
            recommendation = {
                "user": username,
                "reason": " • ".join(reason_parts) if reason_parts else "Strong technical match",
                "search_score": round(hybrid_score, 4),
                "vector_score": round(vector_score, 4),
                "keyword_score": round(bm25_score, 4),
                "languages": languages,
                "topics": topics
            }

            recommendations.append(recommendation)
            logger.info(
                f"@{username} (score: {hybrid_score:.4f}) - {reason_parts[0] if reason_parts else 'Technical match'}")

        logger.info(f"Successfully generated {len(recommendations)} contributor recommendations")

        return {
            "status": "success",
            "recommendations": recommendations,
            "message": f"Found {len(recommendations)} suitable contributors",
            "search_query": search_text,
            "keywords_used": alignment_result.get("keywords", []),
            "technical_domain": alignment_result.get("technical_domain", "other"),
            "search_metadata": {
                "total_candidates": len(results),
                "vector_weight": 0.7,
                "keyword_weight": 0.3,
                "embedding_dimension": len(query_embedding)
            }
        }

    except Exception as e:
        logger.error(f"Error in contributor recommendation: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}
