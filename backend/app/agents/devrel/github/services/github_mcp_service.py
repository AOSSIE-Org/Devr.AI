import os
import requests
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '.env')

load_dotenv(dotenv_path=dotenv_path)

class GitHubMCPService:
    def __init__(self, token: str = None):
        """
        Initializes the GitHub MCP Service.
        It retrieves the GitHub token from the environment variables.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token required; export as GITHUB_TOKEN or place in backend/.env file")
        self.base_url = "https://api.github.com"

    def repo_query(self, owner: str, repo: str) -> dict:

        url = f"{self.base_url}/repos/{owner}/{repo}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DevrAI-GitHubMCPService/0.1"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "message": str(e)}

        data = resp.json()
        
        license_info = data.get("license")
        license_name = license_info.get("name") if license_info else "No license specified"

        return {
            # Core Info
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "html_url": data.get("html_url"),
            "homepage": data.get("homepage"),
            
            # Stats
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "watchers": data.get("watchers_count"),
            "open_issues": data.get("open_issues_count"),
            
            # Details
            "language": data.get("language"),
            "topics": data.get("topics", []),
            "default_branch": data.get("default_branch"),
            "license": license_name,
            
            # Timestamps
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
        }