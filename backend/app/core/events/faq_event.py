from typing import List, Optional
from pydantic import Field
from .base import BaseEvent
from .enums import PlatformType, EventType

class AnswerEvent(BaseEvent):
    """Answer a question event model"""
    platform: PlatformType = PlatformType.FAQ
    organization: Optional[str] = "test"
    question: str = Field(..., title="Question")
    url: Optional[str] = None
    event_type : str = "faq.requested"

class GithubKnowledgeUpdateEvent(BaseEvent):
    """GitHub knowledge base update event model"""
    platform: PlatformType = PlatformType.FAQ
    organization: Optional[str] = "test"
    urls: List[str] = Field(..., description="List of GitHub URLs (api.github.com resources)")
    event_type : str = EventType.GITHUB_KNOWLEDGE_UPDATED

class KnowledgeUpdateEvent(BaseEvent):
    """Knowledge base update event model"""
    platform: PlatformType = PlatformType.FAQ
    organization: Optional[str] = "test"
    content: str = Field(..., description="Content to be stored in the vector database")
    event_type : str = EventType.KNOWLEDGE_UPDATED