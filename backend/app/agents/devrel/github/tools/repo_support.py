import logging
import re
from typing import Dict, Any, Optional
from app.services.codegraph.repo_service import RepoService

logger = logging.getLogger(__name__)


async def handle_repo_support(query: str) -> Dict[str, Any]:
    """Handle repository code graph queries."""
    try:
        service = RepoService()
        repo_name = _extract_repo_name(query)

        if not repo_name:
            return {
                "status": "error",
                "sub_function": "repo_support",
                "message": "Please specify repository: 'Where is X in owner/repo?'"
            }

        result = await service.query_repo(query, repo_name)

        return {
            "status": result["status"],
            "sub_function": "repo_support",
            "repository": repo_name,
            **{k: v for k, v in result.items() if k != "status"}
        }

    except Exception as e:
        logger.exception("Repository support error")
        return {
            "status": "error",
            "sub_function": "repo_support",
            "message": "Query failed. Please try again."
        }

def _extract_repo_name(query: str) -> Optional[str]:
    """Extract repository name from query (owner/repo format)"""
    pattern = r'\b([a-zA-Z0-9][-a-zA-Z0-9]*)/([a-zA-Z0-9_.-]+)\b'
    match = re.search(pattern, query)
    return match.group(0) if match else None
