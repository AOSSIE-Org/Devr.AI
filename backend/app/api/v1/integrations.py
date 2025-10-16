from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from app.models.integration import (
    IntegrationCreateRequest,
    IntegrationUpdateRequest,
    IntegrationResponse,
    IntegrationListResponse,
    IntegrationStatusResponse
)
from app.services.integration_service import integration_service, NotFoundError
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    request: IntegrationCreateRequest,
    user_id: UUID = Depends(get_current_user)
):
    """Create a new organization integration."""
    try:
        return await integration_service.create_integration(user_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/", response_model=IntegrationListResponse)
async def list_integrations(user_id: UUID = Depends(get_current_user)):
    """List all integrations for the current user."""
    try:
        integrations = await integration_service.get_integrations(user_id)
        return IntegrationListResponse(integrations=integrations, total=len(integrations))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get("/status/{platform}", response_model=IntegrationStatusResponse)
async def get_integration_status(
    platform: str,
    user_id: UUID = Depends(get_current_user)
):
    """Get the status of a specific platform integration."""
    try:
        return await integration_service.get_integration_status(user_id, platform)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: UUID,
    user_id: UUID = Depends(get_current_user)
):
    """Get a specific integration."""
    try:
        integration = await integration_service.get_integration(user_id, integration_id)

        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration not found"
            )

        return integration
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    request: IntegrationUpdateRequest,
    user_id: UUID = Depends(get_current_user)
):
    """Update an existing integration."""
    try:
        return await integration_service.update_integration(user_id, integration_id, request)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update integration: {str(e)}"
        ) from e

@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: UUID,
    user_id: UUID = Depends(get_current_user)
):
    """Delete an integration."""
    try:
        await integration_service.delete_integration(user_id, integration_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete integration: {str(e)}"
        ) from e
