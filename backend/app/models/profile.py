"""
Pydantic models for user profile requests and responses.

Defines the data schemas for partial profile updates and full profile representations.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime


class ProfileUpdateRequest(BaseModel):
    """
    Schema for partial user profile updates.

    All fields are optional, allowing consumers to update only the fields
    they wish to modify without overwriting unspecified values.

    Attributes:
        display_name: New public display name of the user.
        name: Alias for display_name for frontend compatibility.
        email: Contact email address.
        bio: Biography or personal description.
        location: Geographic location or time zone.
        avatar_url: URL to user's profile image.
        company: Organization or company name.
        website: Personal or portfolio website URL.
        github: GitHub username or handle.
        twitter: Twitter/X handle.
        role: Primary team or community role.
        social_links: Arbitrary dictionary of extra social links.
    """
    display_name: Optional[str] = Field(None, description="Public display name")
    name: Optional[str] = Field(None, description="Alias for display_name")
    email: Optional[str] = Field(None, description="User email address")
    bio: Optional[str] = Field(None, description="Biography or description")
    location: Optional[str] = Field(None, description="User location")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    company: Optional[str] = Field(None, description="Company or organization")
    website: Optional[str] = Field(None, description="Website URL")
    github: Optional[str] = Field(None, description="GitHub handle")
    twitter: Optional[str] = Field(None, description="Twitter handle")
    role: Optional[str] = Field(None, description="User role")
    social_links: Optional[Dict[str, Any]] = Field(None, description="Additional social links")


class ProfileResponse(BaseModel):
    """
    Schema representing the complete user profile response.

    Attributes:
        id: Unique UUID of the user in Supabase users table.
        display_name: Primary display name.
        name: Alias for display_name for frontend convenience.
        email: User email.
        bio: Short biography.
        location: Geographical location.
        avatar_url: Avatar image URL.
        company: Company name stored in metadata.
        website: Website URL stored in metadata.
        github: Formatted GitHub handle.
        twitter: Twitter handle.
        role: User role.
        social_links: Dictionary of additional social links.
        is_verified: Verification status flag.
        skills: Full dictionary of skills and metadata stored in DB.
        created_at: Record creation timestamp.
        updated_at: Timestamp of last profile modification.
    """
    id: UUID = Field(..., description="Unique user identifier")
    display_name: Optional[str] = Field(None, description="Display name")
    name: Optional[str] = Field(None, description="Alias for display name")
    email: Optional[str] = Field(None, description="Email address")
    bio: Optional[str] = Field(None, description="User biography")
    location: Optional[str] = Field(None, description="Location")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    company: Optional[str] = Field(None, description="Company name")
    website: Optional[str] = Field(None, description="Website URL")
    github: Optional[str] = Field(None, description="GitHub handle")
    twitter: Optional[str] = Field(None, description="Twitter handle")
    role: Optional[str] = Field(None, description="User role")
    social_links: Optional[Dict[str, Any]] = Field(None, description="Social links dictionary")
    is_verified: bool = Field(False, description="Verification status")
    skills: Optional[Dict[str, Any]] = Field(None, description="Skills and metadata JSON document")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
