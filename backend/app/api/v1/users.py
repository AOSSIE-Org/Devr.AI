"""User profile API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from app.core.dependencies import get_current_user
from app.services.auth.management import get_user_by_id, update_user_profile
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    id: str
    email: Optional[str] = None
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    github_username: Optional[str] = None
    discord_username: Optional[str] = None
    slack_username: Optional[str] = None
    preferred_languages: Optional[List[str]] = None


class UserProfileUpdateRequest(BaseModel):
    """Request model for updating user profile."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_languages: Optional[List[str]] = None


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(user_id: UUID = Depends(get_current_user)):
    """Get the current user's profile information."""
    try:
        user = await get_user_by_id(str(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            location=user.location,
            github_username=user.github_username,
            discord_username=user.discord_username,
            slack_username=user.slack_username,
            preferred_languages=user.preferred_languages
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        ) from e


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    request: UserProfileUpdateRequest,
    user_id: UUID = Depends(get_current_user)
):
    """Update the current user's profile information."""
    try:
        # Build update dict from request, excluding None values
        updates = {}
        if request.display_name is not None:
            updates["display_name"] = request.display_name
        if request.bio is not None:
            updates["bio"] = request.bio
        if request.location is not None:
            updates["location"] = request.location
        if request.avatar_url is not None:
            updates["avatar_url"] = request.avatar_url
        if request.preferred_languages is not None:
            updates["preferred_languages"] = request.preferred_languages
        
        if not updates:
            # No updates provided, just return current profile
            user = await get_user_by_id(str(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            return UserProfileResponse(
                id=str(user.id),
                email=user.email,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
                location=user.location,
                github_username=user.github_username,
                discord_username=user.discord_username,
                slack_username=user.slack_username,
                preferred_languages=user.preferred_languages
            )
        
        updated_user = await update_user_profile(str(user_id), **updates)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to update user profile"
            )
        
        return UserProfileResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            display_name=updated_user.display_name,
            avatar_url=updated_user.avatar_url,
            bio=updated_user.bio,
            location=updated_user.location,
            github_username=updated_user.github_username,
            discord_username=updated_user.discord_username,
            slack_username=updated_user.slack_username,
            preferred_languages=updated_user.preferred_languages
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        ) from e
