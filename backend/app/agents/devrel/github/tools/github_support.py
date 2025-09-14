import os
import re
import logging
from app.agents.devrel.github.services import github_mcp_service

logger = logging.getLogger(__name__)

DEFAULT_ORG = os.getenv("GITHUB_ORG", "Aossie-org")

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


async def handle_github_supp(query: str, org: str = None):
    """
    Handles queries related to GitHub repositories and organization stats.
    """
    try:
        repo_name = None

        # --- Try full URL first ---
        match = GH_URL_RE.search(query)
        if match:
            org, repo_name = match.group(1), match.group(2)

        # --- Try owner/repo format ---
        if not repo_name:
            match = OWNER_REPO_RE.search(query)
            if match:
                org, repo_name = match.group(1), match.group(2)

        # --- Try "<name> repo" pattern ---
        if not repo_name:
            match = REPO_NAME_RE.search(query)
            if match:
                repo_name = match.group(1) or match.group(2)
                org = org or DEFAULT_ORG

        # Fallback org if none detected
        org = org or DEFAULT_ORG

        # --- Top repos ---
        if "top" in query and "repo" in query:
            repos = await github_mcp_service.get_org_repositories(org)
            repos = sorted(repos, key=lambda r: r["stars"], reverse=True)[:10]
            return {
                "status": "success",
                "message": f"Top repositories for {org}",
                "repositories": repos,
            }

        # --- Issues, stars, forks, stats ---
        if any(word in query for word in ["issue", "star", "fork", "stat"]):
            if repo_name:
                if "issue" in query:
                    issues = await github_mcp_service.get_repo_issues(org, repo_name)
                    return {
                        "status": "success",
                        "message": f"Open issues for {org}/{repo_name}",
                        "issues": issues,
                    }
                else:
                    repo = await github_mcp_service.get_repo_details(org, repo_name)
                    return {
                        "status": "success",
                        "message": f"Details for {org}/{repo_name}",
                        "repository": repo,
                    }
            else:
                if "stat" in query:
                    stats = await github_mcp_service.get_org_stats(org)
                    return {
                        "status": "success",
                        "message": f"Stats for {org}",
                        "stats": stats,
                    }
                else:
                    repos = await github_mcp_service.get_org_repositories(org)
                    return {
                        "status": "success",
                        "message": f"Repositories for {org}",
                        "repositories": repos,
                    }

        # --- General repo list (fallback) ---
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
        logger.error(f"GitHub support error: {e}")
        return {"status": "error", "message": str(e)}
