from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = FastAPI()

class RepoRequest(BaseModel):
    repo_url: str

def parse_github_url(url: str) -> tuple:
    """Extract owner/repo from GitHub URL"""
    parsed = urlparse(url)
    path = parsed.path.strip('/').split('/')
    if len(path) < 2:
        raise ValueError("Invalid GitHub URL")
    return path[0], path[1]

def github_api_request(endpoint: str) -> dict:
    """Make authenticated GitHub API request"""
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(f"https://api.github.com{endpoint}", headers=headers)
    response.raise_for_status()
    return response.json()


@app.post("/repo-stats")
async def get_repo_stats(repo_url: str):
    try:
        owner, repo_name = parse_github_url(repo_url)
        # Rest of your function...
        # Get basic repo info
        repo_info = github_api_request(f"/repos/{owner}/{repo_name}")
        
        # Get contributors
        contributors = github_api_request(f"/repos/{owner}/{repo_name}/contributors")
        
        # Get pull requests
        prs = github_api_request(f"/repos/{owner}/{repo_name}/pulls?state=all")
        
        # Get issues
        issues = github_api_request(f"/repos/{owner}/{repo_name}/issues?state=all")

        community_profile = github_api_request(f"/repos/{owner}/{repo_name}/community/profile")
        
        # Recent commits (last 5)
        commits = github_api_request(f"/repos/{owner}/{repo_name}/commits?per_page=5")

        code_frequency = github_api_request(f"/repos/{owner}/{repo_name}/stats/code_frequency")
        
        return {
            "name": repo_info["full_name"],
            "stars": repo_info["stargazers_count"],
            "forks": repo_info["forks_count"],
            "watchers": repo_info["subscribers_count"],
            "created_at": repo_info["created_at"],
            "updated_at": repo_info["updated_at"],
             # Licensing and topics
            # "license": repo_info.get("license", {}).get("spdx_id", "No License"),

            "topics": repo_info.get("topics", []),

            "contributors": [{
                "login": c["login"],
                "contributions": c["contributions"],
                "avatar_url": c["avatar_url"]
            } for c in contributors],
            "recent_commits": [{
                "sha": commit["sha"][:7],
                "author": commit["commit"]["author"]["name"],
                "message": commit["commit"]["message"],
                "date": commit["commit"]["author"]["date"]
            } for commit in commits],
            

            "community": {
                "health_percentage": community_profile["health_percentage"],
                "code_of_conduct": community_profile.get("files", {}).get("code_of_conduct") is not None,
                "license": community_profile.get("files", {}).get("license") is not None,
                "readme": community_profile.get("files", {}).get("readme") is not None
            },
             # Issues
            "issues": {
                "total": len(issues),
                "open": sum(1 for issue in issues if issue["state"] == "open"),
                "closed": sum(1 for issue in issues if issue["state"] == "closed"),
                "labels": list({label["name"] for issue in issues for label in issue["labels"]})
            },

             # Code statistics
            "code_activity": {
                "weekly_commits": len(code_frequency) if isinstance(code_frequency, list) else 0,
                "total_additions": sum(week[1] for week in code_frequency) if isinstance(code_frequency, list) else 0,
                "total_deletions": sum(abs(week[2]) for week in code_frequency) if isinstance(code_frequency, list) else 0
            },

             # Pull Requests
            "pull_requests": {
                "total": len(prs),
                "merged": sum(1 for pr in prs if pr["merged_at"]),
                "draft": sum(1 for pr in prs if pr["draft"]),
                "by_state": {
                    "open": sum(1 for pr in prs if pr["state"] == "open"),
                    "closed": sum(1 for pr in prs if pr["state"] == "closed")
                }
            },
        }
        
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, 
                          detail="GitHub API error")
    except ValueError:
        raise HTTPException(status_code=400, 
                          detail="Invalid GitHub URL format")
