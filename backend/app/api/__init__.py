"""
API package for the Devr.AI backend.

This package contains all API-related components:
- router: Main API router with all endpoints
- v1: Version 1 API endpoints
"""

def __getattr__(name: str):
    """
    Dynamically import and return package-level attributes such as api_router.

    Args:
        name: Name of the attribute to retrieve.

    Returns:
        Imported attribute object.

    Raises:
        AttributeError: If attribute is not found.
    """
    if name == "api_router":
        from .router import api_router
        return api_router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["api_router"]

