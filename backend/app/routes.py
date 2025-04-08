from fastapi import APIRouter, HTTPException
from app.models import RepoRequest
from app.utils.github_api import get_repo_stats

router = APIRouter()

@router.post("/repo-stats")
async def repo_stats_endpoint(repo: RepoRequest):
    try:
        return await get_repo_stats(repo.repo_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
