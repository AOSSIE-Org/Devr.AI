import asyncio
import uuid
import logging
import re
from urllib.parse import urlparse
from fastapi import APIRouter, Request, HTTPException, Depends
from uuid import UUID
from app.core.events.event_bus import EventBus
from app.core.events.enums import EventType, PlatformType
from app.core.events.base import BaseEvent
from app.core.handler.handler_registry import HandlerRegistry
from pydantic import BaseModel
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.rate_limiter import get_limiter
from app.core.cache import cache_result
import httpx

router = APIRouter()

# GitHub identifier validation regexes (GitHub allows dots in repo names)
GITHUB_OWNER = re.compile(r'^[a-zA-Z0-9_-]+$')
GITHUB_REPO = re.compile(r'^[a-zA-Z0-9._-]+$')

# Initialize rate limiter
limiter = get_limiter()

class RepoRequest(BaseModel):
    repo_url: str


logging.basicConfig(level=logging.INFO)
handler_registry = HandlerRegistry()
event_bus = EventBus(handler_registry)

# Sample handler function to process events
async def sample_handler(event: BaseEvent):
    logging.info(f"Handler received event: {event.event_type} with data: {event.raw_data}")

# Register all the event handlers for issues and pull requests
def register_event_handlers():
    # Issue events
    event_bus.register_handler(EventType.ISSUE_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_CLOSED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_UPDATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_COMMENTED, sample_handler, PlatformType.GITHUB)
    # Pull request events
    event_bus.register_handler(EventType.PR_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_UPDATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_COMMENTED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_MERGED, sample_handler, PlatformType.GITHUB)

@router.post("/repo-stats")
@limiter.limit("10/minute")
async def get_repo_stats(
    request: Request,
    repo_request: RepoRequest,
    current_user: UUID = Depends(get_current_user)
):
    """
    Get repository statistics from GitHub with rate limiting, caching, and auth.
    
    Rate limit: 10 requests per minute per IP address
    Cache: 5 minutes per repository
    Authentication: Required (Bearer token)
    """
    try:
        # Parse repo URL to extract owner and repo name
        repo_url = repo_request.repo_url.strip()
        
        # Handle SSH format (git@github.com:owner/repo.git)
        if repo_url.startswith("git@"):
            # Split on ':' to get the path part
            if ":" in repo_url:
                path = repo_url.split(":", 1)[1]
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid GitHub repository URL format"
                )
        else:
            # Ensure scheme is present
            if not repo_url.startswith(("http://", "https://")):
                repo_url = "https://" + repo_url
            
            # Parse URL to extract path (excludes query strings and fragments)
            try:
                parsed_url = urlparse(repo_url)
                
                # Verify it's a GitHub URL
                if "github.com" not in parsed_url.netloc:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid GitHub repository URL: must be from github.com"
                    )
                
                # Get path from parsed URL (excludes query string and fragment)
                path = parsed_url.path
                
            except (ValueError, AttributeError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid GitHub repository URL format"
                )
        
        # Strip leading/trailing slashes and .git suffix
        path = path.strip("/").removesuffix(".git")
        
        # Split into segments and validate
        segments = path.split("/")
        if len(segments) < 2:
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub repository URL: expected owner/repo format"
            )
        
        owner, repo = segments[0], segments[1]
        
        # Validate GitHub identifier format (owner and repo)
        if not GITHUB_OWNER.match(owner):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid GitHub owner format: '{owner}'. Must contain only alphanumeric characters, hyphens, and underscores."
            )
        
        if not GITHUB_REPO.match(repo):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid GitHub repository name format: '{repo}'. Must contain only alphanumeric characters, hyphens, dots, and underscores."
            )
        
        # Validate GitHub token is configured
        if not settings.github_token:
            logger = logging.getLogger(__name__)
            logger.error("Error type: MissingConfigurationError")
            raise HTTPException(
                status_code=500,
                detail="GitHub API is not configured. Contact administrator."
            )
        
        # Generate cache key
        cache_key = f"repo_stats:{owner.lower()}_{repo.lower()}"
        
        # Try to get from cache first
        from app.core.cache import get_cache
        cache = get_cache()
        cached_data = cache.get(cache_key)
        if cached_data:
            logging.getLogger(__name__).info(
                f"Serving cached repo stats for {owner}/{repo} (user: {current_user})"
            )
            return cached_data
        
        # Fetch repository stats from GitHub API
        headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Repository not found: {owner}/{repo}"
                    )
                
                if response.status_code == 403:
                    logger = logging.getLogger(__name__)
                    logger.error("Error type: GitHubRateLimitError")
                    raise HTTPException(
                        status_code=503,
                        detail="GitHub API rate limit exceeded. Please try again later."
                    )
                
                if response.status_code != 200:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error type: GitHubAPIError status={response.status_code}")
                    raise HTTPException(
                        status_code=502,
                        detail="GitHub API error. Please try again later."
                    )
                
                repo_data = response.json()
                
                result = {
                    "name": repo_data.get("name"),
                    "full_name": repo_data.get("full_name"),
                    "description": repo_data.get("description"),
                    "stars": repo_data.get("stargazers_count", 0),
                    "forks": repo_data.get("forks_count", 0),
                    "open_issues": repo_data.get("open_issues_count", 0),
                    "language": repo_data.get("language"),
                    "created_at": repo_data.get("created_at"),
                    "updated_at": repo_data.get("updated_at"),
                    "url": repo_data.get("html_url"),
                    "owner": {
                        "login": repo_data.get("owner", {}).get("login"),
                        "avatar_url": repo_data.get("owner", {}).get("avatar_url"),
                    }
                }
                
                # Cache the result for 5 minutes
                cache.set(cache_key, result, ttl_seconds=300)
                
                logger = logging.getLogger(__name__)
                logger.info(
                    f"Fetched repo stats for {owner}/{repo} from GitHub API (user: {current_user})"
                )
                
                return result
            
            except httpx.TimeoutException:
                logger = logging.getLogger(__name__)
                logger.error("Error type: GitHubAPITimeoutError")
                raise HTTPException(
                    status_code=504,
                    detail="GitHub API request timeout. Please try again."
                )
            except httpx.RequestError as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error type: GitHubNetworkError")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to connect to GitHub API. Please try again."
                )
    
    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )


@router.post("/github/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event_header = request.headers.get("X-GitHub-Event")
    logging.info(f"Received GitHub event: {event_header}")

    event_type = None

    # Handle issue events
    if event_header == "issues":
        action = payload.get("action")
        if action == "opened":
            event_type = EventType.ISSUE_CREATED
        elif action == "closed":
            event_type = EventType.ISSUE_CLOSED
        elif action == "edited":
            event_type = EventType.ISSUE_UPDATED

    # Handle issue comment events
    elif event_header == "issue_comment":
        action = payload.get("action")
        if action == "created":
            event_type = EventType.ISSUE_COMMENTED

    # Handle pull request events
    elif event_header == "pull_request":
        action = payload.get("action")
        if action == "opened":
            event_type = EventType.PR_CREATED
        elif action == "edited":
            event_type = EventType.PR_UPDATED
        elif action == "closed":
            # Determine if the PR was merged or simply closed
            if payload.get("pull_request", {}).get("merged"):
                event_type = EventType.PR_MERGED
            else:
                logging.info("Pull request closed without merge; no event dispatched.")

    # Handle pull request comment events
    elif event_header in ["pull_request_review_comment", "pull_request_comment"]:
        action = payload.get("action")
        if action == "created":
            event_type = EventType.PR_COMMENTED

    # Dispatch the event if we have a matching type
    if event_type:
        event = BaseEvent(
            id=str(uuid.uuid4()),
            actor_id=str(payload.get("sender", {}).get("id", "unknown")),
            event_type=event_type,
            platform=PlatformType.GITHUB,
            raw_data=payload
        )
        await event_bus.dispatch(event)
    else:
        logging.info(f"No matching event type for header: {event_header} with action: {payload.get('action')}")

    return {"status": "ok"}
