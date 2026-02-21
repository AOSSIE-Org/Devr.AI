import httpx
from typing import List, Dict

GITHUB_API_BASE = "https://api.github.com"


class IssueSuggestionService:

    def __init__(self, token: str):
        self.token = token

    async def fetch_global_beginner_issues(
        self,
        user_query: str,
        limit: int = 5
    ) -> List[Dict]:

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json"
        }

        # Base GitHub search query
        search_query = 'label:"good first issue" is:issue state:open'

        query_lower = user_query.lower()

        # Language filter
        if "python" in query_lower:
            search_query += " language:python"

        # Org filter
        if "django" in query_lower:
            search_query += " org:django"

        url = f"{GITHUB_API_BASE}/search/issues?q={search_query}&per_page={limit}"

        print("🔍 GitHub Search Query:", search_query)
        print("🔗 GitHub URL:", url)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

            if response.status_code != 200:
                print("❌ GitHub API Error:", response.status_code)
                print("❌ Response Body:", response.text)
                return []

            data = response.json()

        results = []

        for item in data.get("items", []):
            results.append({
                "repo": item["repository_url"].split("/")[-1],
                "number": item["number"],
                "title": item["title"],
                "url": item["html_url"]
            })

        print(f"✅ Found {len(results)} issues")

        return results