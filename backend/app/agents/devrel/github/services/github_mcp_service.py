import os
import requests
import asyncio
from typing import Optional
import config

class GitHubMCPService:
    def __init__(self, token: str = None):
        self.token = token or config.GITHUB_TOKEN
        if not self.token:
            raise ValueError("GitHub token required; export as GITHUB_TOKEN or place in backend/.env file")
        self.base_url = "https://api.github.com"

    def repo_query(self, owner: str, repo: str) -> dict:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        headers = self._headers()
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "message": str(e)}

        data = resp.json()
        license_info = data.get("license")
        license_name = license_info.get("name") if license_info else "No license specified"

        return {
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "html_url": data.get("html_url"),
            "homepage": data.get("homepage"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "watchers": data.get("watchers_count"),
            "open_issues": data.get("open_issues_count"),
            "language": data.get("language"),
            "topics": data.get("topics", []),
            "default_branch": data.get("default_branch"),
            "license": license_name,
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
        }

    def list_repo_issues(self, owner: str, repo: str, state: str = "open") -> list:
        """Fetch issues from a given repository."""
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues?state={state}&per_page=50"
        headers = self._headers()
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "message": str(e)}

        issues = resp.json()
        return [
            {
                "id": i.get("id"),
                "number": i.get("number"),
                "title": i.get("title"),
                "user": i.get("user", {}).get("login"),
                "state": i.get("state"),
                "comments": i.get("comments"),
                "created_at": i.get("created_at"),
                "updated_at": i.get("updated_at"),
                "html_url": i.get("html_url"),
            }
            for i in issues if "pull_request" not in i 
        ]

    def list_org_repos(self, org: str) -> list:
        url = f"{self.base_url}/orgs/{org}/repos?per_page=100&type=all"
        headers = self._headers()
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "message": str(e)}

        repos = resp.json()
        return [
            {
                "name": r.get("name"),
                "full_name": r.get("full_name"),
                "html_url": r.get("html_url"),
                "description": r.get("description"),
                "stars": r.get("stargazers_count", 0),
                "watchers": r.get("watchers_count", 0),
                "forks": r.get("forks_count", 0),
                "language": r.get("language"),
                "updated_at": r.get("updated_at"),
            }
            for r in repos
        ]

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "DevrAI-GitHubMCPService/0.1"
        }


def _get_service(token: Optional[str] = None) -> GitHubMCPService:
    return GitHubMCPService(token=token or config.GITHUB_TOKEN)

async def get_org_repositories(org: str):
    try:
        svc = _get_service()
        return await asyncio.to_thread(svc.list_org_repos, org)
    except Exception as e:
        return {"error": "config_or_request_failed", "message": str(e)}

async def get_org_stats(org: str):
    try:
        svc = _get_service()
        repos = await asyncio.to_thread(svc.list_org_repos, org)
        if isinstance(repos, dict) and "error" in repos:
            return repos
        return {
            "repo_count": len(repos),
            "total_stars": sum(r.get("stars", 0) for r in repos),
            "total_forks": sum(r.get("forks", 0) for r in repos),
        }
    except Exception as e:
        return {"error": "config_or_request_failed", "message": str(e)}

async def get_repo_details(org: str, repo: str):
    try:
        svc = _get_service()
        return await asyncio.to_thread(svc.repo_query, org, repo)
    except Exception as e:
        return {"error": "config_or_request_failed", "message": str(e)}

async def get_repo_issues(org: str, repo: str, state: str = "open"):
    try:
        svc = _get_service()
        return await asyncio.to_thread(svc.list_repo_issues, org, repo, state)
    except Exception as e:
        return {"error": "config_or_request_failed", "message": str(e)}