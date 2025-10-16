from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID


# Request Models
class IntegrationCreateRequest(BaseModel):
    """Request model for registering an organization."""
    platform: Literal["github", "discord", "slack", "discourse"]
    organization_name: str
    organization_link: Optional[str] = None  # GitHub org URL, Discord server ID, etc.
    config: Optional[dict] = None  # Platform-specific data (discord_guild_id, etc.)


class IntegrationUpdateRequest(BaseModel):
    """Request model for updating an integration."""
    organization_name: Optional[str] = None
    organization_link: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[dict] = None


# Response Models
class IntegrationResponse(BaseModel):
    """Response model for integration data."""
    id: UUID
    user_id: UUID
    platform: str
    organization_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    config: Optional[dict] = None
    # Note: We never return the actual token in responses


class IntegrationListResponse(BaseModel):
    """Response model for listing integrations."""
    integrations: list[IntegrationResponse]
    total: int


class IntegrationStatusResponse(BaseModel):
    """Response model for checking integration status."""
    platform: str
    is_connected: bool
    organization_name: Optional[str] = None
    last_updated: Optional[datetime] = None
