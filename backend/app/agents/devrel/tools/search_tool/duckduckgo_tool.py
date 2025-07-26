from ddgs import DDGS

class DuckDuckGoSearchTool:
    async def search(self, query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))

            if not results:
                return "No search results found."

            # Format results for the agent
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'content': result.get('body', ''),
                    'url': result.get('href', '')
                })

            return str(formatted_results)
        except Exception as e:
            return f"Search failed: {str(e)}"
