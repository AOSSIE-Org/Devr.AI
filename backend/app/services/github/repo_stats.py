"""
GitHub Repository Statistics Service.
Fetches comprehensive stats for a GitHub repository including contributors,
pull requests, issues, and commit activity.
"""
import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubRepoStatsService:
    """
    Service to fetch comprehensive statistics for a GitHub repository.
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
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
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

    async def _make_request(self, url: str, params: Dict | None = None) -> Optional[Any]:
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

    async def get_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Fetch basic repository information"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        return await self._make_request(url)

    async def get_contributors(self, owner: str, repo: str, max_contributors: int = 30) -> List[Dict]:
        """Fetch repository contributors"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {"per_page": max_contributors, "anon": "false"}
        contributors = await self._make_request(url, params)
        
        if contributors and isinstance(contributors, list):
            return [
                {
                    "login": c.get("login"),
                    "avatar_url": c.get("avatar_url"),
                    "profile_url": c.get("html_url"),
                    "contributions": c.get("contributions", 0),
                    "type": c.get("type", "User")
                }
                for c in contributors
            ]
        return []

    async def get_pull_requests(self, owner: str, repo: str, state: str = "all", max_prs: int = 50) -> Dict:
        """Fetch pull requests with statistics"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {"state": state, "per_page": max_prs, "sort": "updated", "direction": "desc"}
        prs = await self._make_request(url, params)
        
        if not prs or not isinstance(prs, list):
            return {"open": 0, "closed": 0, "merged": 0, "total": 0, "details": []}

        open_count = 0
        closed_count = 0
        merged_count = 0
        details = []

        for pr in prs:
            pr_state = pr.get("state", "open")
            is_merged = pr.get("merged_at") is not None
            
            if pr_state == "open":
                open_count += 1
                display_state = "open"
            elif is_merged:
                merged_count += 1
                display_state = "merged"
            else:
                closed_count += 1
                display_state = "closed"

            details.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": display_state,
                "url": pr.get("html_url"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "author": {
                    "login": pr.get("user", {}).get("login"),
                    "avatar_url": pr.get("user", {}).get("avatar_url"),
                    "profile_url": pr.get("user", {}).get("html_url")
                },
                "labels": [label.get("name") for label in pr.get("labels", [])],
                "comments": pr.get("comments", 0),
                "draft": pr.get("draft", False)
            })

        return {
            "open": open_count,
            "closed": closed_count,
            "merged": merged_count,
            "total": len(prs),
            "details": details
        }

    async def get_issues(self, owner: str, repo: str, state: str = "all", max_issues: int = 50) -> Dict:
        """Fetch issues (excluding pull requests)"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": max_issues, "sort": "updated", "direction": "desc"}
        issues = await self._make_request(url, params)
        
        if not issues or not isinstance(issues, list):
            return {"open": 0, "closed": 0, "total": 0, "details": []}

        # Filter out pull requests (they appear in issues endpoint too)
        actual_issues = [i for i in issues if "pull_request" not in i]
        
        open_count = sum(1 for i in actual_issues if i.get("state") == "open")
        closed_count = sum(1 for i in actual_issues if i.get("state") == "closed")
        
        details = [
            {
                "number": i.get("number"),
                "title": i.get("title"),
                "state": i.get("state"),
                "url": i.get("html_url"),
                "created_at": i.get("created_at"),
                "author": {
                    "login": i.get("user", {}).get("login"),
                    "avatar_url": i.get("user", {}).get("avatar_url"),
                    "profile_url": i.get("user", {}).get("html_url")
                },
                "labels": [label.get("name") for label in i.get("labels", [])],
                "comments": i.get("comments", 0)
            }
            for i in actual_issues
        ]

        return {
            "open": open_count,
            "closed": closed_count,
            "total": len(actual_issues),
            "details": details
        }

    async def get_commit_activity(self, owner: str, repo: str) -> List[Dict]:
        """Fetch weekly commit activity for the last year"""
        url = f"{self.base_url}/repos/{owner}/{repo}/stats/commit_activity"
        activity = await self._make_request(url)
        
        if activity and isinstance(activity, list):
            # Return last 12 weeks of data
            recent_activity = activity[-12:] if len(activity) > 12 else activity
            return [
                {
                    "week": datetime.fromtimestamp(week.get("week", 0)).strftime("%Y-%m-%d"),
                    "total": week.get("total", 0),
                    "days": week.get("days", [0] * 7)
                }
                for week in recent_activity
            ]
        return []

    async def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch repository languages"""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        languages = await self._make_request(url)
        return languages if languages else {}

    async def get_releases(self, owner: str, repo: str, max_releases: int = 10) -> List[Dict]:
        """Fetch repository releases"""
        url = f"{self.base_url}/repos/{owner}/{repo}/releases"
        params = {"per_page": max_releases}
        releases = await self._make_request(url, params)
        
        if releases and isinstance(releases, list):
            return [
                {
                    "tag_name": r.get("tag_name"),
                    "name": r.get("name"),
                    "published_at": r.get("published_at"),
                    "url": r.get("html_url"),
                    "prerelease": r.get("prerelease", False)
                }
                for r in releases
            ]
        return []

    async def get_comprehensive_stats(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetch comprehensive repository statistics.
        Returns all data needed for the dashboard.
        """
        logger.info(f"Fetching comprehensive stats for {owner}/{repo}")
        
        try:
            # Fetch all data concurrently
            repo_info, contributors, pull_requests, issues, commit_activity, languages, releases = await asyncio.gather(
                self.get_repo_info(owner, repo),
                self.get_contributors(owner, repo),
                self.get_pull_requests(owner, repo),
                self.get_issues(owner, repo),
                self.get_commit_activity(owner, repo),
                self.get_languages(owner, repo),
                self.get_releases(owner, repo),
                return_exceptions=True
            )

            # Handle any exceptions from gather
            if isinstance(repo_info, Exception):
                logger.error(f"Error fetching repo info: {repo_info}")
                repo_info = None
            if isinstance(contributors, Exception):
                logger.error(f"Error fetching contributors: {contributors}")
                contributors = []
            if isinstance(pull_requests, Exception):
                logger.error(f"Error fetching pull requests: {pull_requests}")
                pull_requests = {"open": 0, "closed": 0, "merged": 0, "total": 0, "details": []}
            if isinstance(issues, Exception):
                logger.error(f"Error fetching issues: {issues}")
                issues = {"open": 0, "closed": 0, "total": 0, "details": []}
            if isinstance(commit_activity, Exception):
                logger.error(f"Error fetching commit activity: {commit_activity}")
                commit_activity = []
            if isinstance(languages, Exception):
                logger.error(f"Error fetching languages: {languages}")
                languages = {}
            if isinstance(releases, Exception):
                logger.error(f"Error fetching releases: {releases}")
                releases = []

            if not repo_info:
                raise ValueError(f"Repository {owner}/{repo} not found")

            # Calculate additional metrics
            total_commits = sum(week.get("total", 0) for week in commit_activity) if commit_activity else 0
            
            return {
                "status": "success",
                "repo": f"{owner}/{repo}",
                "repository": {
                    "name": repo_info.get("name"),
                    "full_name": repo_info.get("full_name"),
                    "description": repo_info.get("description"),
                    "url": repo_info.get("html_url"),
                    "stars": repo_info.get("stargazers_count", 0),
                    "forks": repo_info.get("forks_count", 0),
                    "watchers": repo_info.get("watchers_count", 0),
                    "open_issues_count": repo_info.get("open_issues_count", 0),
                    "default_branch": repo_info.get("default_branch"),
                    "created_at": repo_info.get("created_at"),
                    "updated_at": repo_info.get("updated_at"),
                    "pushed_at": repo_info.get("pushed_at"),
                    "topics": repo_info.get("topics", []),
                    "license": repo_info.get("license", {}).get("name") if repo_info.get("license") else None
                },
                "contributors": contributors,
                "pull_requests": pull_requests,
                "issues": issues,
                "commit_activity": commit_activity,
                "languages": languages,
                "releases": releases,
                "metrics": {
                    "total_contributors": len(contributors),
                    "total_commits_recent": total_commits,
                    "stars": repo_info.get("stargazers_count", 0),
                    "forks": repo_info.get("forks_count", 0),
                    "open_prs": pull_requests.get("open", 0),
                    "open_issues": issues.get("open", 0)
                }
            }

        except Exception as e:
            logger.exception(f"Error fetching comprehensive stats for {owner}/{repo}: {str(e)}")
            raise
