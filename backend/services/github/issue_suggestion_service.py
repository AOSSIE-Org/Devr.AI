import httpx
from typing import List, Dict

GITHUB_API_BASE = "https://api.github.com"


class IssueSuggestionService:
    def __init__(self, token: str):
        self.token = token

    async def fetch_global_beginner_issues(
        self,
        language: str = "python",
        limit: int = 5
    ) -> List[Dict]:

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        query = f'label:"good first issue" language:{language} state:open'
        url = f"{GITHUB_API_BASE}/search/issues?q={query}&per_page={limit}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                print("GitHub search failed:", response.text)
                return []

            data = response.json()

        items = data.get("items", [])

        results = []

        for issue in items:
            results.append({
                "number": issue["number"],
                "title": issue["title"],
                "url": issue["html_url"],
                "repo": issue["repository_url"].split("/")[-1]
            })

        return results