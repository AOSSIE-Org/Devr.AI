from typing import List
from pydantic import BaseModel

class ContentRequest(BaseModel):
    content: str

class GithubFileRequest(BaseModel):
    urls: List[str]

class FaqRequest(BaseModel):
    question: str

class FaqResponse(BaseModel):
    answer: str