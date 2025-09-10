import logging
from typing import Dict, Any, Optional
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class GitHubMCPClient:

    #Client for communicating with the GitHub MCP server.
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):

        self.mcp_server_url = mcp_server_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        # Async context manager entry
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Async context manager exit
        if self.session:
            await self.session.close()
    
    async def get_github_supp(self, owner: str, repo: str) -> Dict[str, Any]:

        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        try:
            payload = {
                "owner": owner,
                "repo": repo
            }
            
            async with self.session.post(
                f"{self.mcp_server_url}/github_support",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        return result.get("data", {})
                    else:
                        return {"error": result.get("error", "Unknown error")}
                else:
                    logger.error(f"MCP server error: {response.status}")
                    return {"error": f"MCP server error: {response.status}"}
                    
        except aiohttp.ClientError as e:
            logger.error(f"Error communicating with MCP server: {e}")
            return {"error": f"Communication error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def is_server_available(self) -> bool:
        
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.mcp_server_url}/health", timeout=5) as response:
                return response.status == 200
            
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.debug(f"Health check failed: {e}")
            return False