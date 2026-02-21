from fastapi import APIRouter, HTTPException
from services.github.issue_suggestion_service import IssueSuggestionService
from config import GITHUB_TOKEN, GITHUB_ORG

router = APIRouter()

issue_service = IssueSuggestionService(GITHUB_TOKEN)


@router.get("/beginner-issues")
async def get_beginner_issues(repo: str):
    if not GITHUB_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="GitHub token not configured"
        )

    try:
        issues = await issue_service.fetch_beginner_issues(
            owner=GITHUB_ORG,
            repo=repo
        )

        return {
            "repo": repo,
            "count": len(issues),
            "issues": issues
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch issues: {str(e)}"
        )
