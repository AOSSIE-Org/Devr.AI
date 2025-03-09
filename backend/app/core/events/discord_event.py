from typing import List, Dict, Optional, Any
from pydantic import Field
from .base import BaseEvent
from .enums import PlatformType

class DiscordEvent(BaseEvent):
    """Discord specific event model"""
    platform: PlatformType = PlatformType.DISCORD
    guild_id: str
    channel_id: str
    message_id: Optional[str] = None
    content: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)