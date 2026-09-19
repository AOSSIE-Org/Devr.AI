"""
Tests for ProfileService and Profile API endpoints.

Covers profile retrieval, persistence of updates, clearing fields,
optimistic concurrency with null and non-null updated_at, and API integration roundtrips.
"""

import os
from uuid import uuid4, UUID
from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport

# Set required dummy env vars for test environment
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "dummy-key"

from app.models.profile import ProfileUpdateRequest, ProfileResponse
from app.services.profile_service import ProfileService
from app.api.v1.profile import router as profile_router, profile_service
from app.core.dependencies import get_current_user


class MockExecuteResponse:
    """Mock container for Supabase query execution response."""

    def __init__(self, data):
        """Initialize mock response with data payload."""
        self.data = data


class MockTableQuery:
    """Mock query builder chain for Supabase table operations."""

    def __init__(self, execute_data):
        """Initialize query builder with expected return data."""
        self._execute_data = execute_data
        self.last_update_data = None
        self.applied_eq = {}
        self.applied_is = {}

    def select(self, *args, **kwargs):
        """Mock select call."""
        return self

    def update(self, update_data, *args, **kwargs):
        """Mock update call, merge update_data into persistent row, and record payload."""
        self.last_update_data = update_data
        if self._execute_data and isinstance(self._execute_data[0], dict):
            updated_row = dict(self._execute_data[0])
            for k, v in update_data.items():
                if k == "skills" and isinstance(v, dict) and isinstance(updated_row.get("skills"), dict):
                    merged_skills = dict(updated_row["skills"])
                    merged_skills.update(v)
                    updated_row["skills"] = merged_skills
                else:
                    updated_row[k] = v
            self._execute_data = [updated_row]
        return self

    def eq(self, column, value, *args, **kwargs):
        """Mock eq filter call and record column filter."""
        self.applied_eq[column] = value
        return self

    def is_(self, column, value, *args, **kwargs):
        """Mock is_ filter call and record column filter."""
        self.applied_is[column] = value
        return self

    def limit(self, *args, **kwargs):
        """Mock limit call."""
        return self

    async def execute(self):
        """Execute mock query returning MockExecuteResponse."""
        return MockExecuteResponse(self._execute_data)


@pytest.mark.asyncio
async def test_get_profile_success():
    """Test retrieving a user profile successfully with all mapped fields."""
    user_id = uuid4()
    mock_user = {
        "id": str(user_id),
        "display_name": "Sarah Chen",
        "email": "sarah@example.com",
        "bio": "Open source developer",
        "location": "San Francisco, CA",
        "avatar_url": "https://avatar.url/sarah.png",
        "github_username": "sarahchen",
        "skills": {
            "company": "TechCorp",
            "website": "https://sarahchen.dev",
            "twitter": "@sarahchen_dev",
            "role": "Core Maintainer",
        },
        "is_verified": True,
    }

    service = ProfileService()
    query = MockTableQuery([mock_user])
    service.supabase.table = MagicMock(return_value=query)

    profile = await service.get_profile(user_id)

    assert profile.id == user_id
    assert profile.display_name == "Sarah Chen"
    assert profile.name == "Sarah Chen"
    assert profile.email == "sarah@example.com"
    assert profile.company == "TechCorp"
    assert profile.website == "https://sarahchen.dev"
    assert profile.github == "@sarahchen"
    assert profile.twitter == "@sarahchen_dev"
    assert profile.role == "Core Maintainer"
    assert profile.is_verified is True


@pytest.mark.asyncio
async def test_update_profile_persistence():
    """Test persisting profile updates and metadata into database with re-fetch verification."""
    user_id = uuid4()
    existing_user = {
        "id": str(user_id),
        "display_name": "Old Name",
        "email": "old@example.com",
        "bio": "Old Bio",
        "skills": {"company": "Old Corp"},
        "updated_at": "2026-01-01T00:00:00Z",
    }

    updated_user = {
        "id": str(user_id),
        "display_name": "New Name",
        "email": "new@example.com",
        "bio": "Updated Bio",
        "github_username": "newgithub",
        "skills": {
            "company": "New Corp",
            "website": "https://new.dev",
            "twitter": "@new_twitter",
        },
        "updated_at": "2026-01-02T00:00:00Z",
    }

    service = ProfileService()
    select_query = MockTableQuery([existing_user])
    update_query = MockTableQuery([updated_user])
    refetch_query = MockTableQuery([updated_user])

    service.supabase.table = MagicMock(side_effect=[select_query, update_query, refetch_query])

    update_payload = ProfileUpdateRequest(
        display_name="New Name",
        email="new@example.com",
        bio="Updated Bio",
        company="New Corp",
        website="https://new.dev",
        twitter="@new_twitter",
        github="@newgithub",
    )

    result = await service.update_profile(user_id, update_payload)

    assert result.display_name == "New Name"
    assert result.company == "New Corp"
    assert result.website == "https://new.dev"
    assert result.twitter == "@new_twitter"
    assert result.github == "@newgithub"
    assert update_query.last_update_data is not None
    assert update_query.last_update_data["display_name"] == "New Name"
    assert update_query.last_update_data["github_username"] == "newgithub"
    assert update_query.last_update_data["skills"]["company"] == "New Corp"
    assert update_query.applied_eq["updated_at"] == "2026-01-01T00:00:00Z"
    assert "updated_at" in update_query.last_update_data


@pytest.mark.asyncio
async def test_update_profile_null_updated_at_predicate():
    """Test optimistic concurrency predicate when existing record has null updated_at."""
    user_id = uuid4()
    existing_user = {
        "id": str(user_id),
        "display_name": "Sarah",
        "updated_at": None,
    }

    updated_user = {
        "id": str(user_id),
        "display_name": "Sarah Updated",
        "updated_at": "2026-01-02T00:00:00Z",
    }

    service = ProfileService()
    select_query = MockTableQuery([existing_user])
    update_query = MockTableQuery([updated_user])
    refetch_query = MockTableQuery([updated_user])

    service.supabase.table = MagicMock(side_effect=[select_query, update_query, refetch_query])

    update_payload = ProfileUpdateRequest(display_name="Sarah Updated")
    result = await service.update_profile(user_id, update_payload)

    assert update_query.applied_is["updated_at"] == "null"
    assert result.display_name == "Sarah Updated"


@pytest.mark.asyncio
async def test_update_profile_clear_github_handle():
    """Test that submitting an empty github handle explicitly clears github_username in DB."""
    user_id = uuid4()
    existing_user = {
        "id": str(user_id),
        "display_name": "Sarah",
        "github_username": "sarahchen",
        "skills": {"github": "@sarahchen"},
        "updated_at": "2026-01-01T00:00:00Z",
    }

    cleared_user = {
        "id": str(user_id),
        "display_name": "Sarah",
        "github_username": None,
        "skills": {"github": None},
        "updated_at": "2026-01-02T00:00:00Z",
    }

    service = ProfileService()
    select_query = MockTableQuery([existing_user])
    update_query = MockTableQuery([cleared_user])
    refetch_query = MockTableQuery([cleared_user])

    service.supabase.table = MagicMock(side_effect=[select_query, update_query, refetch_query])

    update_payload = ProfileUpdateRequest(github="")
    result = await service.update_profile(user_id, update_payload)

    assert update_query.last_update_data["github_username"] is None
    assert result.github is None


@pytest.mark.asyncio
async def test_api_endpoints_roundtrip(monkeypatch):
    """Test authenticated GET and PATCH /v1/profile routes verifying persisted fields."""
    test_user_id = uuid4()

    mock_user_db = {
        "id": str(test_user_id),
        "display_name": "Test User",
        "email": "test@example.com",
        "bio": "Testing endpoints",
        "skills": {"company": "Test Co", "website": "https://test.co"},
        "updated_at": "2026-01-01T00:00:00Z",
    }

    app = FastAPI()
    app.include_router(profile_router, prefix="/v1/profile")
    app.dependency_overrides[get_current_user] = lambda: test_user_id

    mock_query = MockTableQuery([mock_user_db])
    monkeypatch.setattr(
        profile_service.supabase,
        "table",
        MagicMock(return_value=mock_query),
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test GET /v1/profile
        get_res = await client.get("/v1/profile")
        assert get_res.status_code == 200
        get_json = get_res.json()
        assert get_json["id"] == str(test_user_id)
        assert get_json["display_name"] == "Test User"
        assert get_json["company"] == "Test Co"

        # 2. Test PATCH /v1/profile with distinct updated response data
        patch_res = await client.patch(
            "/v1/profile",
            json={
                "display_name": "Updated Test User",
                "bio": "New Bio",
                "company": "Updated Co",
            },
        )
        assert patch_res.status_code == 200
        patch_json = patch_res.json()
        assert patch_json["id"] == str(test_user_id)
        assert patch_json["display_name"] == "Updated Test User"
        assert patch_json["bio"] == "New Bio"
        assert patch_json["company"] == "Updated Co"
