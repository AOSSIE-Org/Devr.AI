import logging
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from app.core.config import settings
from app.services.embedding_service.service import EmbeddingService
from app.services.github.user.profiling import GitHubUserProfiler
from app.agents.devrel.github.prompts.contributor_recommendation.issue_summarization import ISSUE_SUMMARIZATION_PROMPT

logger = logging.getLogger(__name__)


class GitHubIssueProcessor:
    """
    A service to fetch, summarize, and embed a GitHub issue.
    """

    def __init__(self, owner: str, repo: str, issue_number: int):
        self.owner = owner
        self.repo = repo
        self.issue_number = issue_number
        self.summarizer_llm = ChatGoogleGenerativeAI(
            model=settings.github_agent_model,
            temperature=0.1,
            google_api_key=settings.gemini_api_key
        )
        self.embedding_service = EmbeddingService()

    async def _fetch_issue_content(self) -> str:
        """
        Fetches and consolidates all text content from a GitHub issue.
        """
        logger.info(f"Fetching content for {self.owner}/{self.repo}#{self.issue_number}")
        async with GitHubUserProfiler() as profiler:
            issue_url = f"{profiler.base_url}/repos/{self.owner}/{self.repo}/issues/{self.issue_number}"
            comments_url = f"{issue_url}/comments"

            issue_data = await profiler._make_request(issue_url)
            if not issue_data:
                raise ValueError("Failed to fetch issue data.")

            content_parts = [
                f"Title: {issue_data['title']}",
                f"Body: {issue_data['body']}",
            ]

            comments_data = await profiler._make_request(comments_url)
            if comments_data:
                comment_texts = [
                    f"Comment by {c['user']['login']}: {c['body']}"
                    for c in comments_data if c.get('body')
                ]
                content_parts.extend(comment_texts)

            return "\n\n---\n\n".join(content_parts)

    async def _summarize_context(self, content: str) -> str:
        """Generates a technical summary of the issue content using an LLM."""
        logger.info(f"Summarizing issue content for {self.owner}/{self.repo}#{self.issue_number}")
        prompt = ISSUE_SUMMARIZATION_PROMPT.format(issue_content=content)
        response = await self.summarizer_llm.ainvoke([HumanMessage(content=prompt)])
        logger.info(f"Generated summary: {response.content.strip()[:100]}")
        return response.content.strip()

    async def get_embedding_for_issue(self) -> List[float]:
        """
        Orchestrates the entire process: fetch, summarize, and embed.
        Returns a vector embedding representing the issue.
        """
        try:
            content = await self._fetch_issue_content()
            if not content:
                raise ValueError("Failed to fetch issue content.")

            summary = await self._summarize_context(content)

            logger.info("Embedding issue summary")
            embedding = await self.embedding_service.get_embedding(summary)
            return embedding
        except Exception as e:
            logger.error(f"Error processing issue {self.owner}/{self.repo}#{self.issue_number}: {str(e)}")
            raise e
