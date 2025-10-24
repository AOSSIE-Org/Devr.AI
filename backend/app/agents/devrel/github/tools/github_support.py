import config
import re
import logging
from typing import Optional
from app.agents.devrel.github.services import github_mcp_service

logger = logging.getLogger(__name__)

DEFAULT_ORG = config.GITHUB_ORG

GH_URL_RE = re.compile(
    r'(?:https?://|git@)github\.com[/:]'
    r'([A-Za-z0-9](?:-?[A-Za-z0-9]){0,38})/'
    r'([A-Za-z0-9._-]+?)(?:\.git)?(?:/|$)',
    re.IGNORECASE,
)

OWNER_REPO_RE = re.compile(
    r'\b([A-Za-z0-9](?:-?[A-Za-z0-9]){0,38})/([A-Za-z0-9._-]{1,100})\b'
)

REPO_NAME_RE = re.compile(
    r'\b(?:repo\s+([A-Za-z0-9._-]+)|([A-Za-z0-9._-]+)\s+repo)\b',
    re.IGNORECASE,
)


async def handle_github_supp(query: str, org: Optional[str] = None):
    """
    Handles queries related to GitHub repositories and organization stats.
    """
    try:
        repo_name = None
        q = query.lower()

        match = GH_URL_RE.search(query)
        if match:
            org, repo_name = match.group(1), match.group(2)

        # owner/repo format 
        if not repo_name:
            match = OWNER_REPO_RE.search(query)
            if match:
                org, repo_name = match.group(1), match.group(2)

        # "<name> repo" pattern
        if not repo_name:
            match = REPO_NAME_RE.search(query)
            if match:
                repo_name = match.group(1) or match.group(2)
                org = org or DEFAULT_ORG

        # Fallback org if none detected
        org = org or DEFAULT_ORG

        # Top repos
        if "top" in q and "repo" in q:
            repos = await github_mcp_service.get_org_repositories(org)
            if isinstance(repos, dict) and "error" in repos:
                return {"status": "error", "message": f"Failed to fetch repositories for {org}", "details": repos}
            repos = sorted(repos, key=lambda r: r.get("stars", 0), reverse=True)[:10]
            return {
                "status": "success",
                "message": f"Top repositories for {org}",
                "repositories": repos,
            }

        # Issues, stars, forks, stats
        if any(word in q for word in ["issue", "star", "fork", "stat", "stats"]):
            if repo_name:
                if "issue" in q:
                    issues = await github_mcp_service.get_repo_issues(org, repo_name)
                    if isinstance(issues, dict) and "error" in issues:
                        return {"status": "error", "message": f"Failed to fetch issues for {org}/{repo_name}", "details": issues}
                    return {"status": "success", "message": f"Open issues for {org}/{repo_name}", "issues": issues}
                else:
                    repo = await github_mcp_service.get_repo_details(org, repo_name)
                    if isinstance(repo, dict) and "error" in repo:
                        return {"status": "error", "message": f"Failed to fetch {org}/{repo_name}", "details": repo}
                    return {"status": "success", "message": f"Details for {org}/{repo_name}", "repository": repo}
            else:
                if any(w in q for w in ["stat", "stats"]):
                    stats = await github_mcp_service.get_org_stats(org)
                    return {
                        "status": "success",
                        "message": f"Stats for {org}",
                        "stats": stats,
                    }
                else:
                    repos = await github_mcp_service.get_org_repositories(org)
                    if isinstance(repos, dict) and "error" in repos:
                        return {"status": "error", "message": f"Failed to fetch repositories for {org}", "details": repos}
                    return {"status": "success", "message": f"Repositories for {org}", "repositories": repos}

        # General repo list 
        repos = await github_mcp_service.get_org_repositories(org)
        if isinstance(repos, dict) and "error" in repos:
            return {
                "status": "error",
                "message": f"Failed to fetch repositories for {org}",
                "details": repos,
            }

        return {
            "status": "success",
            "message": f"Repositories for {org}",
            "repositories": repos,
        }

    except Exception as e:
        logger.exception("GitHub support error: %s", e)
        return {"status": "error", "message": str(e)}
