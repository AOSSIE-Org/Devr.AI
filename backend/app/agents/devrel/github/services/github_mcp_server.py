import os
import logging
import asyncio
import config
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .github_mcp_service import GitHubMCPService
from typing import Optional


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub MCP Server", version="1.0.0")

# Load env vars
GITHUB_ORG = config.GITHUB_ORG
if not GITHUB_ORG:
    logger.warning("GITHUB_ORG not set in .env — defaulting to manual owner input")

github_service: Optional[GitHubMCPService] = None
try:
    token = config.GITHUB_TOKEN
    if not token:
        logger.warning("GITHUB_TOKEN/GH_TOKEN not set; GitHub API calls may be rate-limited or fail.")
    github_service = GitHubMCPService(token=token)
    logger.info("GitHub service initialized successfully")
except Exception as e:
    logger.exception("Failed to initialize GitHub service")
    github_service = None

class RepoInfoRequest(BaseModel):
    repo: str 
    owner: Optional[str] = None

class RepoInfoResponse(BaseModel):
    status: str
    data: dict
    error: str = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "github-mcp"}

class OrgInfoRequest(BaseModel):
    org: str

@app.post("/list_org_repos")
async def list_org_repos(request: OrgInfoRequest):
    try:
        if not github_service:
            raise HTTPException(status_code=503, detail="GitHub service not available")

        result = await asyncio.to_thread(github_service.list_org_repos, request.org)

        if "error" in result:
            return {"status": "error", "data": {}, "error": result["error"]}

        return {"status": "success", "data": result}

    except Exception as e:
        logger.exception("Error listing org repos")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/github_support")
async def get_github_supp(request: RepoInfoRequest):
    """Get repo details, using fixed org from env"""
    if not github_service:
        raise HTTPException(status_code=503, detail="GitHub service not available")
    owner = request.owner or GITHUB_ORG
    if not owner:
        raise HTTPException(status_code=400, detail="Missing owner; provide 'owner' or set GITHUB_ORG")

    try:
        result = await asyncio.to_thread(github_service.repo_query, owner, request.repo)
        if "error" in result:
            return RepoInfoResponse(status="error", data={}, error=result["error"])
        return RepoInfoResponse(status="success", data=result)
    except Exception as e:
        logger.exception("Error getting repo info")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
