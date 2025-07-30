from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from app.agents.devrel.tools.search_tool.duckduckgo_tool import DuckDuckGoSearchTool

class DuckDuckGoSearchInput(BaseModel):
    query: str = Field(..., description="Search query")

class DuckDuckGoSearchLangTool(BaseTool):
    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo"
    args_schema: Type[BaseModel] = DuckDuckGoSearchInput

    def _run(self, query: str) -> str:
        tool = DuckDuckGoSearchTool()
        return tool.search(query)

    async def _arun(self, query: str) -> str:
        tool = DuckDuckGoSearchTool()
        return await tool.search(query)
        # Use .search here, NOT .run or ._run
