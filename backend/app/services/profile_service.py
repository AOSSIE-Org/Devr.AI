"""
Profile Service.

Handles fetching and updating user profiles with database persistence
using Supabase async client.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.database.supabase.client import get_supabase_client
from app.models.profile import ProfileUpdateRequest, ProfileResponse

logger = logging.getLogger(__name__)


class ProfileService:
    """Service layer for profile management operations."""

    def __init__(self):
        """Initialize the profile service with the shared Supabase async client."""
        self.supabase = get_supabase_client()

    def _map_user_to_response(self, user_data: Dict[str, Any]) -> ProfileResponse:
        """
        Map a database row from the users table to a ProfileResponse schema.

        Args:
            user_data: Dict containing user record from Supabase users table.

        Returns:
            ProfileResponse instance.
        """
        skills = user_data.get("skills")
        if not isinstance(skills, dict):
            skills = {}

        display_name = user_data.get("display_name") or ""
        github_val = skills.get("github")
        if github_val is None and user_data.get("github_username"):
            github_val = f"@{user_data['github_username']}"

        return ProfileResponse(
            id=UUID(user_data["id"]) if isinstance(user_data["id"], str) else user_data["id"],
            display_name=display_name,
            name=display_name,
            email=user_data.get("email"),
            bio=user_data.get("bio"),
            location=user_data.get("location"),
            avatar_url=user_data.get("avatar_url"),
            company=skills.get("company"),
            website=skills.get("website"),
            github=github_val,
            twitter=skills.get("twitter"),
            role=skills.get("role"),
            social_links=skills.get("social_links"),
            is_verified=user_data.get("is_verified", False),
            skills=skills,
            created_at=user_data.get("created_at"),
            updated_at=user_data.get("updated_at"),
        )

    async def get_profile(self, user_id: UUID) -> ProfileResponse:
        """
        Fetch user profile by user UUID from Supabase.

        Args:
            user_id: Unique UUID of the user.

        Returns:
            ProfileResponse with profile details.

        Raises:
            HTTPException: 404 if user not found, 500 on database failure.
        """
        try:
            response = await self.supabase.table("users").select("*").eq("id", str(user_id)).limit(1).execute()
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found",
                )
            return self._map_user_to_response(response.data[0])
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve profile",
            ) from e

    async def update_profile(
        self,
        user_id: UUID,
        update_req: ProfileUpdateRequest,
        max_retries: int = 3,
    ) -> ProfileResponse:
        """
        Update user profile in Supabase database with optimistic concurrency control.

        Applies partial updates to native columns and merges extra metadata
        into the skills JSON document, clearing empty values when explicitly submitted.

        Args:
            user_id: Unique UUID of the user.
            update_req: ProfileUpdateRequest with fields to update.
            max_retries: Number of retry attempts on concurrent collision.

        Returns:
            ProfileResponse reflecting the refreshed persisted state.

        Raises:
            HTTPException: 404 if user not found, 500 on write failure.
        """
        for attempt in range(max_retries):
            try:
                # 1. Fetch current profile state
                response = await self.supabase.table("users").select("*").eq("id", str(user_id)).limit(1).execute()
                if not response.data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User profile not found",
                    )
                current_user = response.data[0]
                prev_updated_at = current_user.get("updated_at")

                update_data: Dict[str, Any] = {}

                if update_req.display_name is not None:
                    update_data["display_name"] = update_req.display_name
                elif update_req.name is not None:
                    update_data["display_name"] = update_req.name

                if update_req.email is not None:
                    update_data["email"] = update_req.email

                if update_req.bio is not None:
                    update_data["bio"] = update_req.bio

                if update_req.location is not None:
                    update_data["location"] = update_req.location

                if update_req.avatar_url is not None:
                    update_data["avatar_url"] = update_req.avatar_url

                # Explicitly clear or set github_username
                if update_req.github is not None:
                    cleaned_github = update_req.github.lstrip("@").strip()
                    update_data["github_username"] = cleaned_github if cleaned_github else None

                # 2. Merge metadata into skills JSON document
                skills = current_user.get("skills")
                if not isinstance(skills, dict):
                    skills = {}
                skills = dict(skills)

                skills_updated = False
                if update_req.company is not None:
                    skills["company"] = update_req.company
                    skills_updated = True
                if update_req.website is not None:
                    skills["website"] = update_req.website
                    skills_updated = True
                if update_req.twitter is not None:
                    skills["twitter"] = update_req.twitter
                    skills_updated = True
                if update_req.github is not None:
                    cleaned = update_req.github.lstrip("@").strip()
                    skills["github"] = f"@{cleaned}" if cleaned else None
                    skills_updated = True
                if update_req.role is not None:
                    skills["role"] = update_req.role
                    skills_updated = True
                if update_req.social_links is not None:
                    skills["social_links"] = update_req.social_links
                    skills_updated = True

                if skills_updated:
                    update_data["skills"] = skills

                update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

                # 3. Perform atomic update with optimistic concurrency predicate applied on every attempt
                query = self.supabase.table("users").update(update_data).eq("id", str(user_id))
                if prev_updated_at is not None:
                    query = query.eq("updated_at", prev_updated_at)
                else:
                    query = query.is_("updated_at", "null")

                update_response = await query.execute()

                # If optimistic check failed due to concurrent update, retry
                if not update_response.data:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Concurrent collision updating profile for {user_id}, retrying ({attempt + 1}/{max_retries})"
                        )
                        continue
                    else:
                        logger.error(f"Failed to update profile for user {user_id} after {max_retries} attempts")
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to update profile due to concurrent modification",
                        )

                # 4. Re-fetch persisted state to verify finalized write
                refetched = await self.supabase.table("users").select("*").eq("id", str(user_id)).limit(1).execute()
                persisted_row = refetched.data[0] if refetched.data else update_response.data[0]

                logger.info(f"Successfully persisted profile update for user: {user_id}")
                return self._map_user_to_response(persisted_row)

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error updating profile for user {user_id}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update profile",
                ) from e

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )
