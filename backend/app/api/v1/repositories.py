from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.codegraph.repo_service import RepoService
import traceback

router = APIRouter(prefix="/api", tags=["repositories"])

class RepoRequest(BaseModel):
    repo_url: str

@router.post("/repo-stats")
async def analyze_repository(request: RepoRequest):
    print(f" repo aa gayi : {request.repo_url}")

    try:
        result = await RepoService().index_repo(request.repo_url)
        return {
            "message": "Repository indexed successfully",
            "repository": request.repo_url,
            "stats": result
        }
    except Exception as e:
        print(traceback.format_exc()) 
        raise HTTPException(status_code=500, detail=str(e)) from e
