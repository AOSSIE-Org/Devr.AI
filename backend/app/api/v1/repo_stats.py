"""
Repository stats endpoint for analyzing GitHub repositories.
"""
import logging
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.github.repo_stats import GitHubRepoStatsService

logger = logging.getLogger(__name__)

router = APIRouter()


class RepoStatsRequest(BaseModel):
    repo_url: str


class AuthorInfo(BaseModel):
    login: str | None = None
    avatar_url: str | None = None
    profile_url: str | None = None


class ContributorInfo(BaseModel):
    login: str | None = None
    avatar_url: str | None = None
    profile_url: str | None = None
    contributions: int = 0
    type: str = "User"


class PullRequestDetail(BaseModel):
    number: int
    title: str
    state: str
    url: str
    created_at: str | None = None
    updated_at: str | None = None
    author: AuthorInfo
    labels: List[str] = []
    comments: int = 0
    draft: bool = False


class PullRequestStats(BaseModel):
    open: int = 0
    closed: int = 0
    merged: int = 0
    total: int = 0
    details: List[PullRequestDetail] = []


class IssueDetail(BaseModel):
    number: int
    title: str
    state: str
    url: str
    created_at: str | None = None
    author: AuthorInfo
    labels: List[str] = []
    comments: int = 0


class IssueStats(BaseModel):
    open: int = 0
    closed: int = 0
    total: int = 0
    details: List[IssueDetail] = []


class CommitActivity(BaseModel):
    week: str
    total: int = 0
    days: List[int] = []


class ReleaseInfo(BaseModel):
    tag_name: str
    name: str | None = None
    published_at: str | None = None
    url: str | None = None
    prerelease: bool = False


class RepositoryInfo(BaseModel):
    name: str
    full_name: str
    description: str | None = None
    url: str
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues_count: int = 0
    default_branch: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    pushed_at: str | None = None
    topics: List[str] = []
    license: str | None = None


class Metrics(BaseModel):
    total_contributors: int = 0
    total_commits_recent: int = 0
    stars: int = 0
    forks: int = 0
    open_prs: int = 0
    open_issues: int = 0


class RepoStatsResponse(BaseModel):
    status: str
    repo: str | None = None
    message: str | None = None
    repository: RepositoryInfo | None = None
    contributors: List[ContributorInfo] = []
    pull_requests: PullRequestStats | None = None
    issues: IssueStats | None = None
    commit_activity: List[CommitActivity] = []
    languages: Dict[str, int] = {}
    releases: List[ReleaseInfo] = []
    metrics: Metrics | None = None


def parse_repo_url(repo_input: str) -> tuple[str, str]:
    """Parse repository URL or owner/repo format"""
    repo_input = repo_input.strip().rstrip('/').rstrip('.git')

    patterns = [
        (r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', 'url'),
        (r'^([a-zA-Z0-9][-a-zA-Z0-9]*)/([a-zA-Z0-9._-]+)$', 'short')
    ]

    for pattern, _ in patterns:
        match = re.search(pattern, repo_input)
        if match:
            owner, repo = match.groups()
            return owner, repo

    raise ValueError(
        f"Invalid repository format: '{repo_input}'. "
        "Expected: 'owner/repo' or 'https://github.com/owner/repo'"
    )


@router.post("/repo-stats", response_model=RepoStatsResponse)
async def analyze_repository(request: RepoStatsRequest):
    """
    Analyze a GitHub repository and return comprehensive stats.
    
    Returns contributors, pull requests, issues, commit activity,
    languages, and other repository metrics.
    """
    try:
        logger.info(f"Received repo-stats request for: {request.repo_url}")
        
        # Parse the repository URL
        try:
            owner, repo = parse_repo_url(request.repo_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        
        logger.info(f"Fetching stats for {owner}/{repo}")
        
        # Fetch comprehensive stats from GitHub
        async with GitHubRepoStatsService() as stats_service:
            result = await stats_service.get_comprehensive_stats(owner, repo)
        
        logger.info(f"Successfully fetched stats for {owner}/{repo}")
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.exception(f"Value error: {e}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Error analyzing repository: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze repository: {str(e)}"
        ) from e
