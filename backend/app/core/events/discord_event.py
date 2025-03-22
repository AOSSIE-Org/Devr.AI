from typing import List, Dict, Optional, Any
from pydantic import Field
from .base import BaseEvent
from .enums import PlatformType

class DiscordEvent(BaseEvent):
    """Discord specific event model"""
    platform: PlatformType = PlatformType.DISCORD
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    message_id: Optional[str] = None
    content: Optional[str] = None
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        """Ensure event data is properly initialized from raw_data"""
        raw_data = data.get("raw_data", {})

        super().__init__(
            id=data.get("id"),
            event_type=data.get("event_type"),
            platform=PlatformType.DISCORD,
            actor_id=data.get("actor_id") or raw_data.get("actor_id"),
            actor_name=data.get("actor_name"),
            raw_data=raw_data,
            metadata=data.get("metadata", {}),
            guild_id=raw_data.get("guild_id"),
            message_id=raw_data.get("id"),
            content=raw_data.get("content"),
            channel_id=data.get("channel_id"),
        )
