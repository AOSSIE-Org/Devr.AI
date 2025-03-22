from typing import List, Dict, Optional, Any
from pydantic import Field
from .base import BaseEvent
from .enums import PlatformType

class SlackEvent(BaseEvent):
    """Slack specific event model"""
    platform: PlatformType = PlatformType.SLACK
    team_id: str
    channel_id: str
    message_ts: Optional[str] = None
    text: Optional[str] = None
    thread_ts: Optional[str] = None
    blocks: List[Dict[str, Any]] = Field(default_factory=list)