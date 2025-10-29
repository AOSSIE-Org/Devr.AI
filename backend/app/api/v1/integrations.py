from fastapi import APIRouter, Depends, status
from uuid import UUID
from app.models.integration import (
    IntegrationCreateRequest,
    IntegrationUpdateRequest,
    IntegrationResponse,
    IntegrationListResponse,
    IntegrationStatusResponse
)
from app.services.integration_service import integration_service, IntegrationNotFoundError
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    ValidationError,
    ResourceNotFoundError,
    DatabaseError,
    ExternalServiceError
)
from app.core.logging_config import get_logger, log_performance

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
@log_performance("create_integration")
async def create_integration(
    request: IntegrationCreateRequest,
    user_id: UUID = Depends(get_current_user)
):
    """Create a new organization integration."""
    logger.info(f"Creating integration for user {user_id}, platform: {request.platform}")
    
    try:
        integration = await integration_service.create_integration(user_id, request)
        logger.info(f"Successfully created integration {integration.id} for user {user_id}")
        return integration
        
    except ValueError as e:
        logger.warning(f"Validation error creating integration: {str(e)}")
        raise ValidationError(str(e), context={"user_id": str(user_id), "platform": request.platform})
        
    except Exception as e:
        logger.error(f"Unexpected error creating integration: {str(e)}")
        raise DatabaseError("Failed to create integration", context={"user_id": str(user_id)})


@router.get("/", response_model=IntegrationListResponse)
@log_performance("list_integrations")
async def list_integrations(user_id: UUID = Depends(get_current_user)):
    """List all integrations for the current user."""
    logger.info(f"Listing integrations for user {user_id}")
    
    try:
        integrations = await integration_service.get_integrations(user_id)
        logger.info(f"Found {len(integrations)} integrations for user {user_id}")
        return IntegrationListResponse(integrations=integrations, total=len(integrations))
        
    except Exception as e:
        logger.error(f"Error listing integrations for user {user_id}: {str(e)}")
        raise DatabaseError("Failed to retrieve integrations", context={"user_id": str(user_id)})


@router.get("/status/{platform}", response_model=IntegrationStatusResponse)
@log_performance("get_integration_status")
async def get_integration_status(
    platform: str,
    user_id: UUID = Depends(get_current_user)
):
    """Get the status of a specific platform integration."""
    logger.info(f"Getting integration status for user {user_id}, platform: {platform}")
    
    try:
        status_response = await integration_service.get_integration_status(user_id, platform)
        logger.info(f"Retrieved status for platform {platform}, user {user_id}")
        return status_response
        
    except Exception as e:
        logger.error(f"Error getting integration status: {str(e)}")
        raise ExternalServiceError(
            service_name=platform,
            detail="Failed to retrieve integration status",
            context={"user_id": str(user_id), "platform": platform}
        )


@router.get("/{integration_id}", response_model=IntegrationResponse)
@log_performance("get_integration")
async def get_integration(
    integration_id: UUID,
    user_id: UUID = Depends(get_current_user)
):
    """Get a specific integration."""
    logger.info(f"Getting integration {integration_id} for user {user_id}")
    
    try:
        integration = await integration_service.get_integration(user_id, integration_id)

        if not integration:
            logger.warning(f"Integration {integration_id} not found for user {user_id}")
            raise ResourceNotFoundError("Integration", str(integration_id))

        logger.info(f"Successfully retrieved integration {integration_id}")
        return integration
        
    except ResourceNotFoundError:
        raise
        
    except Exception as e:
        logger.error(f"Error getting integration {integration_id}: {str(e)}")
        raise DatabaseError("Failed to retrieve integration", context={"integration_id": str(integration_id)})


@router.put("/{integration_id}", response_model=IntegrationResponse)
@log_performance("update_integration")
async def update_integration(
    integration_id: UUID,
    request: IntegrationUpdateRequest,
    user_id: UUID = Depends(get_current_user)
):
    """Update an existing integration."""
    logger.info(f"Updating integration {integration_id} for user {user_id}")
    
    try:
        integration = await integration_service.update_integration(user_id, integration_id, request)
        logger.info(f"Successfully updated integration {integration_id}")
        return integration
        
    except IntegrationNotFoundError as e:
        logger.warning(f"Integration {integration_id} not found for update: {str(e)}")
        raise ResourceNotFoundError("Integration", str(integration_id))
        
    except ValueError as e:
        logger.warning(f"Validation error updating integration {integration_id}: {str(e)}")
        raise ValidationError(str(e), context={"integration_id": str(integration_id)})
        
    except Exception as e:
        logger.error(f"Error updating integration {integration_id}: {str(e)}")
        raise DatabaseError("Failed to update integration", context={"integration_id": str(integration_id)})


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
@log_performance("delete_integration")
async def delete_integration(
    integration_id: UUID,
    user_id: UUID = Depends(get_current_user)
):
    """Delete an integration."""
    logger.info(f"Deleting integration {integration_id} for user {user_id}")
    
    try:
        await integration_service.delete_integration(user_id, integration_id)
        logger.info(f"Successfully deleted integration {integration_id}")
        
    except IntegrationNotFoundError as e:
        logger.warning(f"Integration {integration_id} not found for deletion: {str(e)}")
        raise ResourceNotFoundError("Integration", str(integration_id))
        
    except ValueError as e:
        logger.warning(f"Validation error deleting integration {integration_id}: {str(e)}")
        raise ValidationError(str(e), context={"integration_id": str(integration_id)})
        
    except Exception as e:
        logger.error(f"Error deleting integration {integration_id}: {str(e)}")
        raise DatabaseError("Failed to delete integration", context={"integration_id": str(integration_id)})
