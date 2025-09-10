from ..services.github_mcp_client import GitHubMCPClient
import re

GH_URL_RE = re.compile(
    r'(?:https?://|git@)github\.com[/:]'
    r'([A-Za-z0-9](?:-?[A-Za-z0-9]){0,38})/'
    r'([A-Za-z0-9._-]+?)(?:\.git)?(?:/|$)',
    re.IGNORECASE,
)

OWNER_REPO_RE = re.compile(
    r'\b([A-Za-z0-9](?:-?[A-Za-z0-9]){0,38})/([A-Za-z0-9._-]{1,100})\b'
)

async def handle_github_supp(user_query: str) -> dict:
    m = GH_URL_RE.search(user_query) or OWNER_REPO_RE.search(user_query)
    if not m:
        return {"status": "error", "message": "Usage: include a GitHub owner/repo (e.g., AOSSIE-Org/Devr.AI) or a GitHub URL."}

    owner, repo = m.group(1), m.group(2)
    
    #GitHub MCP client to communicate with the MCP server
    async with GitHubMCPClient() as client:
        if not await client.is_server_available():
            return {
                "status": "error", 
                "message": "GitHub MCP server not available. Please ensure the MCP server is running."
            }
        
        result = await client.get_github_supp(owner, repo)
        
        if "error" in result:
            return {
                "status": "error", 
                "owner": owner, 
                "repo": repo, 
                "message": result["error"]
            }
        
        return {
            "status": "success", 
            "owner": owner, 
            "repo": repo, 
            "data": result
        }
