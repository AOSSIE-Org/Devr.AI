import os
from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_ratelimiter import RedisDependencyMarker, RedisSettings, RateLimiter
from fastapi_ratelimiter.ratelimiting import RateLimitExceeded

# Configure Redis settings
redis_settings = RedisSettings(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
)

# Initialize the rate limiter
rate_limiter = RateLimiter(
    redis_settings=redis_settings,
    default_limits=["1000 per day", "100 per hour"],
    default_limits_per_method=True,
    default_limits_exempt_when=lambda request: request.method == "OPTIONS",
)

async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions with a JSON response."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": f"Rate limit exceeded. Try again in {exc.retry_after} seconds.",
            "retry_after": exc.retry_after,
        },
        headers={"Retry-After": str(exc.retry_after)},
    )

def get_user_identifier(request: Request) -> str:
    """Extract user identifier from request for rate limiting."""
    # Try to get user ID from JWT or session
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        return f"user:{token[:8]}"  # Simplified token-based identifier
    
    # Fall back to IP-based rate limiting
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"

def setup_rate_limiter(app: FastAPI):
    """Set up rate limiting for the FastAPI application."""
    # Add rate limiter middleware
    app.add_middleware(rate_limiter.middleware)
    app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
    
    # Add rate limiter to app state for easy access in routes
    app.state.rate_limiter = rate_limiter