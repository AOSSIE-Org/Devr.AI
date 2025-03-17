from typing import List, Optional
from pydantic import Field
from .base import BaseEvent
from .enums import PlatformType

class GitHubEvent(BaseEvent):
    """GitHub specific event model"""
    platform: PlatformType = PlatformType.GITHUB
    repository: str
    organization: Optional[str] = None
    issue_number: Optional[int] = None
    pr_number: Optional[int] = None
    labels: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    body: Optional[str] = None
    url: Optional[str] = None