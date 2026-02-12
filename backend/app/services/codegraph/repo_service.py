import logging
import aiohttp
import re
from typing import Dict, Any
from datetime import datetime
from app.database.supabase.client import get_supabase_client
import os

logger = logging.getLogger(__name__)


class RepoService:
    """Service for repository code graph operations using code-graph-backend"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.backend_url = os.getenv("CODEGRAPH_BACKEND_URL", "http://localhost:5000")
        self.secret_token = os.getenv("SECRET_TOKEN", "DevRAI_CodeGraph_Secret")
        self.indexing_timeout = aiohttp.ClientTimeout(total=3600, connect=60)
        self.query_timeout = aiohttp.ClientTimeout(total=300, connect=30)
        logger.info(f"RepoService initialized with backend: {self.backend_url}")

    def _parse_repo_url(self, repo_input: str) -> Dict[str, str]:
        """Parse repository URL or owner/repo format"""
        repo_input = repo_input.strip().rstrip('/').rstrip('.git')

        patterns = [
            (r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', 'url'),
            (r'^([a-zA-Z0-9][-a-zA-Z0-9]*)/([a-zA-Z0-9._-]+)$', 'short')
        ]

        for pattern, _ in patterns:
            match = re.search(pattern, repo_input)
            if match:
                owner, repo = match.groups()
                return {
                    "owner": owner,
                    "repo": repo,
                    "full_name": f"{owner}/{repo}"
                }

        raise ValueError(
            f"Invalid repository format: '{repo_input}'. "
            "Expected: 'owner/repo' or 'https://github.com/owner/repo'"
        )

    async def index_repo(self, repo_input: str, discord_id: str) -> Dict[str, Any]:
        """Index a GitHub repository."""
        try:
            # Parse repository URL
            repo_info = self._parse_repo_url(repo_input)
            github_url = f"https://github.com/{repo_info['full_name']}"
            graph_name = repo_info['repo']

            logger.info(f"Indexing request: {repo_info['full_name']} -> graph: {graph_name}")

            # Check if already indexed
            existing = await self.supabase.table("indexed_repositories").select("*").eq(
                "repository_full_name", repo_info['full_name']
            ).eq("is_deleted", False).execute()

            if existing.data:
                repo_data = existing.data[0]
                status = repo_data['indexing_status']

                if status == 'completed':
                    # Return existing data as success instead of error
                    return {
                        "status": "success",
                        "repo": repo_info['full_name'],
                        "graph_name": repo_data['graph_name'],
                        "nodes": repo_data.get('node_count', 0),
                        "edges": repo_data.get('edge_count', 0),
                        "message": "Repository already indexed."
                    }
                elif status == 'pending':
                    return {
                        "status": "pending",
                        "repo": repo_info['full_name'],
                        "graph_name": repo_data['graph_name'],
                        "message": "Repository indexing in progress. Please wait."
                    }
                # If failed, we'll allow re-indexing by updating the existing record

                # Update existing failed record
                logger.info(f"Updating existing failed record for {repo_info['full_name']}")
                await self.supabase.table("indexed_repositories").update({
                    "indexing_status": "pending",
                    "last_error": None,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", repo_data['id']).execute()
            else:
                # Insert new record
                logger.info(f"Creating new record for {repo_info['full_name']}")
                await self.supabase.table("indexed_repositories").insert({
                    "repository_full_name": repo_info['full_name'],
                    "graph_name": graph_name,
                    "indexing_status": "pending",
                    "indexed_by_discord_id": discord_id,
                    "last_error": None
                }).execute()

            logger.info(f"Calling code-graph-backend: {self.backend_url}/analyze_repo")

            # Call code-graph-backend to index repository
            async with aiohttp.ClientSession(timeout=self.indexing_timeout) as session:
                async with session.post(
                    f"{self.backend_url}/analyze_repo",
                    json={
                        "repo_url": github_url,
                        "ignore": [
                            "./.git", "./.github", "./node_modules", "./venv",
                            "./.venv", "./build", "./dist", "./__pycache__",
                            "./target", "./.pytest_cache", "./.mypy_cache",
                            "./.tox", "./coverage", "./.coverage", "./htmlcov"
                        ]
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": self.secret_token
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json() if await response.text() else {}

                        await self.supabase.table("indexed_repositories").update({
                            "indexing_status": "completed",
                            "indexed_at": datetime.now().isoformat(),
                            "node_count": data.get("node_count", 0),
                            "edge_count": data.get("edge_count", 0),
                            "last_error": None
                        }).eq("repository_full_name", repo_info['full_name']).eq(
                            "is_deleted", False
                        ).execute()

                        return {
                            "status": "success",
                            "repo": repo_info['full_name'],
                            "graph_name": graph_name,
                            "nodes": data.get("node_count", 0),
                            "edges": data.get("edge_count", 0)
                        }
                    else:
                        error_msg = (await response.text())[:500]

                        await self.supabase.table("indexed_repositories").update({
                            "indexing_status": "failed",
                            "last_error": error_msg
                        }).eq("repository_full_name", repo_info['full_name']).eq(
                            "is_deleted", False
                        ).execute()

                        return {"status": "error", "message": f"Indexing failed: {error_msg}"}

        except ValueError as e:
            return {"status": "error", "message": str(e)}
        except aiohttp.ClientError as e:
            logger.exception(f"Network error indexing {repo_input}: {e}")
            return {"status": "error", "message": "Network error. Please try again."}
        except Exception:
            logger.exception(f"Failed to index {repo_input}")
            return {"status": "error", "message": "Indexing failed. Please contact support."}

    async def query_repo(self, question: str, repo_full_name: str) -> Dict[str, Any]:
        """
        Query an indexed repository using natural language.

        Args:
            question: Natural language question about the code
            repo_full_name: Repository in format 'owner/repo'

        Returns:
            Dict with status and answer
        """
        try:
            result = await self.supabase.table("indexed_repositories").select(
                "graph_name, indexing_status"
            ).eq(
                "repository_full_name", repo_full_name
            ).eq("is_deleted", False).execute()

            if not result.data:
                logger.warning(f"Repository not found: {repo_full_name}")
                return {
                    "status": "not_indexed",
                    "message": (
                        f"Repository `{repo_full_name}` is not indexed. "
                        "Use `/index_repository` to index it first."
                    )
                }

            repo_data = result.data[0]

            if repo_data['indexing_status'] != 'completed':
                status = repo_data['indexing_status']
                return {
                    "status": "not_ready",
                    "message": f"Repository status: {status}. Please wait for indexing to complete."
                }

            graph_name = repo_data['graph_name']
            logger.info(f"Querying graph: {graph_name}")

            async with aiohttp.ClientSession(timeout=self.query_timeout) as session:
                async with session.post(
                    f"{self.backend_url}/chat",
                    json={
                        "repo": repo_data['graph_name'],
                        "msg": question
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": self.secret_token
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        answer = data.get("response")

                        if not answer:
                            return {
                                "status": "error",
                                "message": "No response received. Try rephrasing your question."
                            }

                        return {
                            "status": "success",
                            "answer": answer,
                            "cypher": data.get("cypher_query", "")
                        }
                    else:
                        error_text = (await response.text())[:200]
                        logger.error(f"Query failed [{response.status}]: {error_text}")
                        return {
                            "status": "error",
                            "message": "Query failed. Please try again or rephrase your question."
                        }

        except aiohttp.ClientError as e:
            logger.exception(f"Network error querying {repo_full_name}: {e}")
            return {"status": "error", "message": "Network error. Please try again."}
        except Exception:
            logger.exception(f"Failed to query {repo_full_name}")
            return {"status": "error", "message": "Query failed. Please contact support."}

    async def delete_repo(self, repo_full_name: str, discord_id: str) -> Dict[str, Any]:
        """Delete an indexed repository."""
        try:
            logger.info(f"Delete request: {repo_full_name} by {discord_id}")

            result = await self.supabase.table("indexed_repositories").select("*").eq(
                "repository_full_name", repo_full_name
            ).eq("is_deleted", False).execute()

            if not result.data:
                return {"status": "error", "message": "Repository not found"}

            graph_name = result.data[0]["graph_name"]

            async with aiohttp.ClientSession(timeout=self.query_timeout) as session:
                async with session.post(
                    f"{self.backend_url}/delete_graph",
                    json={"graph_name": graph_name},
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": self.secret_token
                    }
                ) as response:
                    if response.status != 200:
                        error_text = (await response.text())[:200]
                        logger.error(f"Backend delete failed [{response.status}]: {error_text}")
                        return {
                            "status": "error",
                            "message": "Failed to delete graph from backend. Please contact support."
                        }

            await self.supabase.table("indexed_repositories").update({
                "is_deleted": True,
                "updated_at": datetime.now().isoformat()
            }).eq("repository_full_name", repo_full_name).eq("is_deleted", False).execute()

            return {"status": "success", "repo": repo_full_name, "graph_name": graph_name}

        except Exception:
            logger.exception(f"Failed to delete {repo_full_name}")
            return {"status": "error", "message": "Deletion failed. Please contact support."}

    async def list_repos(self, discord_id: str) -> list:
        """List indexed repositories for a user."""
        try:
            result = await self.supabase.table("indexed_repositories").select("*").eq(
                "indexed_by_discord_id", discord_id
            ).eq("is_deleted", False).order("created_at", desc=True).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"List repos error: {e}", exc_info=True)
            return []
