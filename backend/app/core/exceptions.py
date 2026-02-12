"""
Custom exception classes for better error handling across the application.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException


class BaseAPIException(HTTPException):
    """Base exception class for API errors with additional context."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}


class ValidationError(BaseAPIException):
    """Raised when request validation fails."""
    
    def __init__(self, detail: str, field: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="VALIDATION_ERROR",
            context={"field": field, **(context or {})}
        )


class AuthenticationError(BaseAPIException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed", context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            context=context
        )


class AuthorizationError(BaseAPIException):
    """Raised when authorization fails."""
    
    def __init__(self, detail: str = "Insufficient permissions", context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
            context=context
        )


class ResourceNotFoundError(BaseAPIException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        detail = f"{resource_type} not found"
        if resource_id:
            detail += f" (ID: {resource_id})"
        
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND",
            context={"resource_type": resource_type, "resource_id": resource_id, **(context or {})}
        )


class ConflictError(BaseAPIException):
    """Raised when a resource conflict occurs."""
    
    def __init__(self, detail: str, resource_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code="CONFLICT_ERROR",
            context={"resource_type": resource_type, **(context or {})}
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=429,
            detail=detail,
            error_code="RATE_LIMIT_ERROR",
            context={"retry_after": retry_after, **(context or {})}
        )


class ExternalServiceError(BaseAPIException):
    """Raised when external service integration fails."""
    
    def __init__(self, service_name: str, detail: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        detail = detail or f"{service_name} service is currently unavailable"
        super().__init__(
            status_code=502,
            detail=detail,
            error_code="EXTERNAL_SERVICE_ERROR",
            context={"service_name": service_name, **(context or {})}
        )


class ServiceUnavailableError(BaseAPIException):
    """Raised when a service is temporarily unavailable."""
    
    def __init__(self, detail: str = "Service temporarily unavailable", retry_after: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=503,
            detail=detail,
            error_code="SERVICE_UNAVAILABLE",
            context={"retry_after": retry_after, **(context or {})}
        )


class DatabaseError(BaseAPIException):
    """Raised when database operations fail."""
    
    def __init__(self, detail: str = "Database operation failed", operation: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            detail=detail,
            error_code="DATABASE_ERROR",
            context={"operation": operation, **(context or {})}
        )


class ConfigurationError(BaseAPIException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, detail: str, config_key: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            detail=detail,
            error_code="CONFIGURATION_ERROR",
            context={"config_key": config_key, **(context or {})}
        )


# Integration-specific exceptions
class IntegrationError(BaseAPIException):
    """Base class for integration-related errors."""
    pass


class IntegrationNotFoundError(ResourceNotFoundError):
    """Raised when an integration is not found."""
    
    def __init__(self, integration_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            resource_type="Integration",
            resource_id=integration_id,
            context=context
        )


class IntegrationConfigError(ValidationError):
    """Raised when integration configuration is invalid."""
    
    def __init__(self, platform: str, detail: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            detail=f"Invalid {platform} integration configuration: {detail}",
            context={"platform": platform, **(context or {})}
        )


class GitHubAPIError(ExternalServiceError):
    """Raised when GitHub API calls fail."""
    
    def __init__(self, detail: Optional[str] = None, status_code: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            service_name="GitHub",
            detail=detail,
            context={"github_status_code": status_code, **(context or {})}
        )


class DiscordAPIError(ExternalServiceError):
    """Raised when Discord API calls fail."""
    
    def __init__(self, detail: Optional[str] = None, status_code: Optional[int] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            service_name="Discord",
            detail=detail,
            context={"discord_status_code": status_code, **(context or {})}
        )


class WeaviateError(ExternalServiceError):
    """Raised when Weaviate operations fail."""
    
    def __init__(self, detail: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            service_name="Weaviate",
            detail=detail,
            context=context
        )


class SupabaseError(ExternalServiceError):
    """Raised when Supabase operations fail."""
    
    def __init__(self, detail: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            service_name="Supabase",
            detail=detail,
            context=context
        )