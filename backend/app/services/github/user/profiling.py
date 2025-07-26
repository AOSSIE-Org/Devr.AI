import logging
import asyncio
import aiohttp
from typing import List, Optional, Dict
from datetime import datetime
from collections import Counter
from app.models.database.weaviate import WeaviateUserProfile, WeaviateRepository, WeaviatePullRequest
from app.database.weaviate.operations import store_user_profile
from app.services.embedding_service.service import EmbeddingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubUserProfiler:
    """
    Class to handle GitHub user profiling and Weaviate storage.
    Uses organization's GitHub token to fetch public user data via GitHub REST API.
    """

    def __init__(self):
        if not settings.github_token:
            raise ValueError("GitHub token not configured in environment variables")

        self.headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DevRel-AI-Bot/1.0"
        }
        self.base_url = "https://api.github.com"
        self.session = None

    async def __aenter__(self):
        """Create async HTTP session"""
        timeout = aiohttp.ClientTimeout(total=60, connect=10, sock_read=30)
        connector = aiohttp.TCPConnector(
            limit=50,  # Total connection pool size
            limit_per_host=10,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )

        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=timeout,
            connector=connector
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close async HTTP session"""
        if self.session:
            await self.session.close()

    async def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make a GET request to GitHub API"""
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    logger.warning(f"GitHub API 404: {url}")
                    return None
                elif response.status == 403:
                    logger.error(f"GitHub API rate limit exceeded: {url}")
                    return None
                else:
                    logger.error(f"GitHub API error {response.status}: {url}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout accessing GitHub API: {url}")
            return None
        except Exception as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return None

    async def request(self, url: str, params: Dict | None = None) -> Optional[Dict]:
        """Public, stable wrapper around the internal HTTP helper."""
        return await self._make_request(url, params)

    async def get_user_data(self, github_username: str) -> Optional[Dict]:
        """Fetch user data"""
        url = f"{self.base_url}/users/{github_username}"
        user_data = await self._make_request(url)

        if user_data:
            logger.info(f"Successfully fetched user data for {github_username}")
        else:
            logger.error(f"Failed to fetch user data for {github_username}")

        return user_data

    async def get_user_repositories(self, github_username: str, max_repos: int = 50) -> List[Dict]:
        """Fetch user repositories"""
        try:
            params = {
                "type": "owner",
                "sort": "updated",
                "direction": "desc",
                "per_page": max_repos
            }

            url = f"{self.base_url}/users/{github_username}/repos"
            repos = await self._make_request(url, params)

            if repos and isinstance(repos, list):
                logger.info(f"Successfully fetched {len(repos)} repositories for {github_username}")
                return repos
            else:
                logger.info(f"No repositories found for {github_username}")
                return []

        except Exception as e:
            logger.error(f"Error fetching repositories for {github_username}: {str(e)}")
            return []

    async def get_repository_languages(self, languages_url: str) -> List[str]:
        """Fetch repository languages"""
        try:
            languages_data = await self._make_request(languages_url)
            if languages_data and isinstance(languages_data, dict):
                return list(languages_data.keys())
            return []
        except Exception as e:
            logger.warning(f"Error fetching languages from {languages_url}: {str(e)}")
            return []

    async def get_user_pull_requests(self, github_username: str, max_prs: int = 100) -> List[WeaviatePullRequest]:
        """Fetch pull requests"""
        try:
            params = {
                "q": f"author:{github_username} is:pr",
                "sort": "created",
                "order": "desc",
                "per_page": max_prs
            }

            url = f"{self.base_url}/search/issues"
            search_result = await self._make_request(url, params)

            if not search_result or "items" not in search_result:
                logger.info(f"No pull requests found for {github_username}")
                return []

            items = search_result["items"]
            pull_requests = []

            for pr_data in items:
                try:
                    repo_name = "unknown"
                    if pr_data.get("html_url"):
                        url_parts = pr_data["html_url"].split('/')
                        if len(url_parts) >= 5:
                            repo_name = f"{url_parts[3]}/{url_parts[4]}"

                    merged_at = None
                    if pr_data.get("pull_request") and pr_data["pull_request"].get("merged_at"):
                        merged_at = pr_data["pull_request"]["merged_at"]

                    pr_obj = WeaviatePullRequest(
                        title=pr_data["title"],
                        body=pr_data.get("body", "")[:500] if pr_data.get("body") else "",
                        state=pr_data["state"],
                        repository=repo_name,
                        created_at=pr_data.get("created_at"),
                        closed_at=pr_data.get("closed_at"),
                        merged_at=merged_at,
                        labels=[label["name"] for label in pr_data.get("labels", [])],
                        url=pr_data["html_url"]
                    )
                    pull_requests.append(pr_obj)

                except Exception as e:
                    logger.warning(f"Error processing pull request: {str(e)}")
                    continue

            logger.info(f"Successfully fetched {len(pull_requests)} pull requests for {github_username}")
            return pull_requests

        except Exception as e:
            logger.error(f"Error fetching pull requests for {github_username}: {str(e)}")
            return []

    async def _process_repository(self, repo_data: Dict) -> Optional[WeaviateRepository]:
        """Process a single repository"""
        try:
            languages = []
            if repo_data.get("languages_url"):
                languages = await self.get_repository_languages(repo_data["languages_url"])

            return WeaviateRepository(
                name=repo_data["name"],
                description=repo_data.get("description"),
                url=repo_data["html_url"],
                languages=languages,
                stars=repo_data.get("stargazers_count", 0),
                forks=repo_data.get("forks_count", 0)
            )
        except Exception as e:
            logger.warning(f"Error processing repository {repo_data.get('name', 'unknown')}: {str(e)}")
            return None

    def analyze_language_frequency(self, repositories: List[WeaviateRepository]) -> List[str]:
        """
        Analyze language frequency across repositories to identify top 5 languages.
        """
        language_counter = Counter()
        for repo in repositories:
            language_counter.update(repo.languages)

        top_languages = language_counter.most_common(5)
        logger.info(f"Top 5 languages by frequency: {top_languages}")
        return [lang for lang, _ in top_languages]

    async def build_user_profile(self, user_id: str, github_username: str) -> Optional[WeaviateUserProfile]:
        """
        Build a complete user profile for Weaviate indexing
        """
        logger.info(f"Building user profile for GitHub user: {github_username}")

        # Run user data, repositories, and pull requests fetch concurrently
        user_task = self.get_user_data(github_username)
        repos_task = self.get_user_repositories(github_username)
        prs_task = self.get_user_pull_requests(github_username)

        try:
            user_data, repos_data, pull_requests = await asyncio.gather(
                user_task, repos_task, prs_task, return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Error in concurrent data fetching: {str(e)}")
            return None

        if isinstance(user_data, Exception) or not user_data:
            logger.error(f"Could not fetch user data for {github_username}")
            return None

        if isinstance(repos_data, Exception):
            logger.warning(f"Error fetching repositories: {repos_data}")
            repos_data = []

        if isinstance(pull_requests, Exception):
            logger.warning(f"Error fetching pull requests: {pull_requests}")
            pull_requests = []

        logger.info(f"Found {len(repos_data)} repositories and {len(pull_requests)} pull requests for {github_username}")

        repository_tasks = [self._process_repository(repo) for repo in repos_data]

        repositories = []
        if repository_tasks:
            try:
                repo_results = await asyncio.gather(*repository_tasks, return_exceptions=True)
                repositories = [r for r in repo_results if r is not None and not isinstance(r, Exception)]
            except Exception as e:
                logger.warning(f"Error processing repositories: {str(e)}")

        all_languages = set()
        all_topics = set()
        total_stars = 0
        total_forks = 0

        for repo_obj in repositories:
            all_languages.update(repo_obj.languages)
            total_stars += repo_obj.stars
            total_forks += repo_obj.forks

        for repo_data in repos_data:
            topics = repo_data.get("topics", [])
            if topics:
                all_topics.update(topics)

        top_languages = self.analyze_language_frequency(repositories)

        profile = WeaviateUserProfile(
            user_id=user_id,
            github_username=github_username,
            display_name=user_data.get("name"),
            bio=user_data.get("bio"),
            location=user_data.get("location"),
            repositories=repositories,
            pull_requests=pull_requests,
            languages=top_languages,
            topics=list(all_topics),
            followers_count=user_data.get("followers", 0),
            following_count=user_data.get("following", 0),
            total_stars_received=total_stars,
            total_forks=total_forks,
            profile_text_for_embedding="",  # Will be filled by embedding service
            last_updated=datetime.now()
        )

        logger.info(
            f"Successfully built profile for {github_username}: "
            f"{len(repositories)} repos, {len(top_languages)} top languages, "
            f"{len(pull_requests)} pull requests analyzed"
        )
        return profile


async def profile_user_from_github(user_id: str, github_username: str) -> bool:
    """Profile a user, generate embeddings, and store in Weaviate."""

    async with GitHubUserProfiler() as profiler:
        try:
            profile = await profiler.build_user_profile(user_id, github_username)
            if not profile:
                logger.error(f"Failed to build profile for {github_username}")
                return False

            logger.info(f"Processing profile for embedding: {github_username}")
            embedding_service = EmbeddingService()

            try:
                processed_profile, embedding_vector = await embedding_service.process_user_profile(profile)
                logger.info(f"Successfully generated profile summary for {github_username}")

                success = await store_user_profile(processed_profile, embedding_vector)
                if success:
                    logger.info(f"Successfully stored profile for user {github_username} with embeddings")
                else:
                    logger.error(f"Failed to store profile for user {github_username} in Weaviate")
                return success

            except Exception as e:
                logger.error(f"Error processing profile with embedding service for {github_username}: {str(e)}")
                return False
            finally:
                embedding_service.clear_cache()

        except Exception as e:
            logger.error(f"Failed to profile user {github_username}: {str(e)}")
            return False
