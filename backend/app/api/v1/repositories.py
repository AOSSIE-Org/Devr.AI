import logging
# import traceback

from app.services.codegraph.repo_service import RepoService
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["repositories"])


class RepoRequest(BaseModel):
    repo_url: str


@router.post("/repo-stats")
async def analyze_repository(request: RepoRequest):
    logger.info(f"Repository analysis requested: {request.repo_url}")

    try:
        result = await RepoService().index_repo(request.repo_url)
        return {
            "message": "Repository indexed successfully",
            "repository": request.repo_url,
            "stats": result,
        }
    except ValueError as e:
        logger.warning(f"Invalid repository URL: {request.repo_url} - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception(f"Failed to index repository: {request.repo_url}")
        raise HTTPException(status_code=500, detail=str(e)) from e
