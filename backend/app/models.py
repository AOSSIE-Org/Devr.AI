from pydantic import BaseModel

class RepoRequest(BaseModel):
    repo_url: str
