"""
Input validation and sanitization middleware for API security.
Prevents XSS, SQL injection, and validates request payloads.
"""
import html
import re
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from pydantic import BaseModel, Field, validator
import logging

logger = logging.getLogger(__name__)

# Validation schemas
class MessageRequest(BaseModel):
    """Schema for message requests with validation"""
    content: str = Field(..., min_length=1, max_length=2000)
    user_id: str = Field(..., regex=r'^[0-9]+$')
    channel_id: Optional[str] = Field(None, regex=r'^[0-9]+$')
    thread_id: Optional[str] = Field(None, regex=r'^[0-9]+$')
    platform: str = Field(..., regex=r'^(discord|slack|github)$')
    
    @validator('content')
    def sanitize_content(cls, v):
        """Sanitize content to prevent XSS attacks"""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        # Remove dangerous HTML/script tags
        sanitized = html.escape(v)
        # Additional sanitization for markdown injection
        sanitized = re.sub(r'[<>]', '', sanitized)
        return sanitized.strip()

class UserIDRequest(BaseModel):
    """Schema for user ID validation"""
    user_id: str = Field(..., regex=r'^[0-9a-fA-F-]{36}$|^[0-9]+$')
    
class SessionRequest(BaseModel):
    """Schema for session validation"""
    session_id: str = Field(..., regex=r'^[0-9a-fA-F-]{36}$')
    
class RepositoryRequest(BaseModel):
    """Schema for repository URL validation"""
    repo_url: str = Field(..., regex=r'^https://github\.com/[\w-]+/[\w.-]+/?$')
    
    @validator('repo_url')
    def validate_github_url(cls, v):
        """Ensure URL is a valid GitHub repository"""
        if not v.startswith('https://github.com/'):
            raise ValueError('Only GitHub repositories are supported')
        return v.rstrip('/')

# Sanitization utilities
def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent injection attacks.
    
    Args:
        value: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Trim to max length
    sanitized = value[:max_length]
    
    # Escape HTML entities
    sanitized = html.escape(sanitized)
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    sanitized = ''.join(char for char in sanitized 
                       if char == '\n' or char == '\t' or ord(char) >= 32)
    
    return sanitized.strip()

def sanitize_dict(data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
    """
    Recursively sanitize dictionary values.
    
    Args:
        data: Dictionary to sanitize
        max_depth: Maximum nesting depth to prevent DoS
        
    Returns:
        Sanitized dictionary
    """
    if max_depth <= 0:
        return {}
    
    sanitized = {}
    for key, value in data.items():
        # Sanitize key
        clean_key = sanitize_string(str(key), max_length=100)
        
        if isinstance(value, str):
            sanitized[clean_key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[clean_key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, (list, tuple)):
            sanitized[clean_key] = [
                sanitize_string(str(item)) if isinstance(item, str) else item
                for item in value[:100]  # Limit array size
            ]
        else:
            sanitized[clean_key] = value
            
    return sanitized

async def validate_request_size(request: Request, max_size: int = 1_000_000):
    """
    Middleware to validate request body size.
    
    Args:
        request: FastAPI request object
        max_size: Maximum body size in bytes (default 1MB)
    """
    content_length = request.headers.get('content-length')
    
    if content_length:
        content_length = int(content_length)
        if content_length > max_size:
            logger.warning(f"Request body too large: {content_length} bytes")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Maximum size: {max_size} bytes"
            )

def validate_user_id(user_id: str) -> bool:
    """
    Validate user ID format (Discord snowflake or UUID).
    
    Args:
        user_id: User ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Discord snowflake (numeric) or UUID format
    discord_pattern = r'^[0-9]{17,19}$'
    uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    
    return bool(re.match(discord_pattern, user_id) or re.match(uuid_pattern, user_id))

def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format (UUID v4).
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
    return bool(re.match(pattern, session_id))

# SQL Injection prevention
def escape_sql_like(value: str) -> str:
    """
    Escape special characters for SQL LIKE queries.
    
    Args:
        value: String to escape
        
    Returns:
        Escaped string safe for SQL LIKE
    """
    # Escape SQL LIKE wildcards
    value = value.replace('\\', '\\\\')
    value = value.replace('%', '\\%')
    value = value.replace('_', '\\_')
    return value

class ValidationMiddleware:
    """Middleware for comprehensive input validation"""
    
    def __init__(self, max_body_size: int = 1_000_000):
        self.max_body_size = max_body_size
        
    async def __call__(self, request: Request, call_next):
        """Process request with validation"""
        try:
            # Validate body size
            await validate_request_size(request, self.max_body_size)
            
            # Continue to next middleware
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Validation middleware error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request format"
            )
