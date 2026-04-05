import httpx
import logging
import os
from typing import Type, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)

# --- TOOL 1: INDEXING ---
class FalkorIndexInput(BaseModel):
    repo_url: str = Field(description="The full GitHub URL or 'owner/repo' string to index.")

class FalkorIndexTool(BaseTool):
    name: str = "falkor_index_tool"
    description: str = "Indexes a public GitHub repository so it can be queried."
    args_schema: Type[BaseModel] = FalkorIndexInput

    async def _arun(self, repo_url: str) -> str:
        if not settings.codegraph_backend_url:
            return "Error: CODEGRAPH_BACKEND_URL not set."
        
        if "github.com" not in repo_url:
            repo_url = f"https://github.com/{repo_url}"

        secret_token = os.getenv("SECRET_TOKEN", "DevRAI_CodeGraph_Secret")

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                url = f"{settings.codegraph_backend_url}/analyze_repo"
                logger.info(f"Indexing {repo_url} at {url}")
                
                response = await client.post(
                    url,
                    json={"repo_url": repo_url},
                    headers={"Authorization": secret_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return f"Successfully indexed. Nodes: {data.get('node_count', 0)}"
                else:
                    return f"Indexing failed: {response.text}"
        except Exception as e:
            return f"Error triggering index: {str(e)}"

    def _run(self, repo_url: str) -> str: return "Async only."

# --- TOOL 2: QUERYING ---
class FalkorQueryInput(BaseModel):
    query: str = Field(description="Natural language query.")
    repo_name: Optional[str] = Field(description="The repo name to query (e.g. 'Devr.AI').")

class FalkorCodeGraphTool(BaseTool):
    name: str = "falkor_code_graph_tool"
    description: str = "Queries the code graph. Input should be a natural language query."
    args_schema: Type[BaseModel] = FalkorQueryInput

    async def _arun(self, query: str, repo_name: str = "Devr.AI") -> str:
        if not settings.codegraph_backend_url: return "Error: Backend URL missing."
        secret_token = os.getenv("SECRET_TOKEN", "DevRAI_CodeGraph_Secret")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                url = f"{settings.codegraph_backend_url}/chat"
                payload = {"repo": repo_name, "msg": query}
                headers = {"Authorization": secret_token}
                
                logger.info(f"Querying {repo_name}: {query}")
                
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 401: return "Error: Unauthorized Token."
                if response.status_code != 200: return f"Error: {response.text}"
                
                data = response.json()
                return f"Answer: {data.get('response', 'No response')}"

        except Exception as e:
            return f"Query failed: {str(e)}"

    def _run(self, query: str, repo_name: str = "Devr.AI") -> str: return "Async only."