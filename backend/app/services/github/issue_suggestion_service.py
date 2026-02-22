import httpx
import re
from typing import List, Dict

GITHUB_API_BASE = "https://api.github.com"


class IssueSuggestionService:
    def __init__(self, token: str):
        self.token = token

    async def fetch_beginner_issues(
        self,
        language: str = "python",
        limit: int = 5,
    ) -> List[Dict]:
        """
        Fetch global beginner-friendly GitHub issues
        filtered by programming language.
        """

        # -----------------------------
        # Validate & clamp limit
        # GitHub Search API allows max 100
        # -----------------------------
        limit = max(1, min(limit, 100))

        # -----------------------------
        # Normalize & validate language
        # Allow: C++, C#, Objective-C, Jupyter Notebook
        # Block dangerous query-breaking characters
        # -----------------------------
        language = (language or "").strip()

        if not language or re.search(r'[:"\'`|&$<>]', language):
            language = "python"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        search_query = (
            f'label:"good first issue" '
            f'is:issue state:open '
            f'language:{language}'
        )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{GITHUB_API_BASE}/search/issues",
                    headers=headers,
                    params={
                        "q": search_query,
                        "per_page": limit
                    }
                )

            if response.status_code != 200:
                return []

            data = response.json()

            return [
                {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "url": item.get("html_url"),
                    "repo": item.get("repository_url", "").split("/")[-1],
                }
                for item in data.get("items", [])
            ]

        except Exception:
            # Fail gracefully without crashing the app
            return []