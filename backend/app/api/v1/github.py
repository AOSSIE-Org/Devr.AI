from fastapi import APIRouter, HTTPException
from app.services.github.issue_suggestion_service import IssueSuggestionService
from app.core.config import settings

router = APIRouter()


@router.get("/beginner-issues")
async def get_beginner_issues(
    language: str = "python",
    limit: int = 5
):
    """
    Fetch global beginner-friendly GitHub issues.
    """

    token = settings.github_token_resolved

    if not token:
        raise HTTPException(
            status_code=500,
            detail="GitHub token not configured"
        )

    issue_service = IssueSuggestionService(token)

    try:
        issues = await issue_service.fetch_beginner_issues(
            language=language,
            limit=limit
        )

        return {
            "language": language,
            "count": len(issues),
            "issues": issues
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch beginner issues"
        ) from e