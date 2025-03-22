from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class BaseEvent(BaseModel):
    """Base event model for all platform events"""
    id: str = Field(..., description="Unique identifier for the event")
    platform: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the event")
    channel_id: str | None = None
    actor_id: str = Field(..., description="ID of the user who triggered the event")
    actor_name: Optional[str] = Field(None, description="Name of the user who triggered the event")
    raw_data: Dict[str, Any] = Field({}, description="Raw event data from the platform")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata for the event")
    content: Optional[str] = Field(None, description="Content of the event")

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEvent":
        """Create event from dictionary"""
        return cls(**data)
