import os
import logging
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .github_mcp_service import GitHubMCPService
from typing import Optional

dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub MCP Server", version="1.0.0")

github_service: Optional[GitHubMCPService] = None
try:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN/GH_TOKEN not set; GitHub API calls may be rate-limited or fail.")
    github_service = GitHubMCPService(token=token)
    logger.info("GitHub service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize GitHub service: {e}")
    github_service = None

class RepoInfoRequest(BaseModel):
    owner: str
    repo: str

class RepoInfoResponse(BaseModel):
    status: str
    data: dict
    error: str = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "github-mcp"}

@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """MCP protocol endpoint"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "get_github_supp":
                owner = arguments.get("owner")
                repo = arguments.get("repo")
                
                if not owner or not repo:
                    return {"error": "Missing owner or repo parameter"}
                
                if not github_service:
                    return {"error": "GitHub service not available"}
                result = github_service.repo_query(owner, repo)
                return {"result": result}
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        else:
            return {"error": f"Unknown method: {method}"}
            
    except Exception as e:
        logger.exception("Error in MCP endpoint")
        return {"error": str(e)}

@app.post("/github_support")
async def get_github_supp(request: RepoInfoRequest):

    try:
        if not github_service:
            raise HTTPException(status_code=500, detail="GitHub service not available")
        
        result = github_service.repo_query(request.owner, request.repo)
        
        if "error" in result:
            return RepoInfoResponse(status="error", data={}, error=result["error"])
        
        return RepoInfoResponse(status="success", data=result)
        
    except Exception as e:
        logger.error(f"Error getting repo info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
