from fastapi import Header, HTTPException, status, Request
from uuid import UUID
from app.database.supabase.client import get_supabase_client
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import DevRAIApplication

logger = logging.getLogger(__name__)


def get_app_instance(request: Request) -> "DevRAIApplication":
    """Get the application instance from FastAPI app state."""
    return request.app.state.app_instance


async def get_current_user(authorization: str = Header(None)) -> UUID:
    """
    Get the current authenticated user from the Supabase JWT token.

    Args:
        authorization: The Authorization header containing the Bearer token

    Returns:
        UUID: The user's ID

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")

    try:
        supabase = get_supabase_client()
        # Verify the token and get user
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UUID(user_response.user.id)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Authentication error")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
