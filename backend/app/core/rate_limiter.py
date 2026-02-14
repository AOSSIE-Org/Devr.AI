"""
Rate limiting configuration using slowapi.
Prevents API quota exhaustion and protects against abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

# Initialize the global rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],  # Default fallback limit
    storage_uri="memory://",  # Use in-memory storage (can upgrade to Redis)
)


def get_limiter() -> Limiter:
    """Get the global rate limiter instance."""
    return limiter
