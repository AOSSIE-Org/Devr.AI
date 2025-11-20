from fastapi import APIRouter, Request, Depends
from fastapi_ratelimiter import rate_limiter

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/unlimited")
async def unlimited():
    """Unlimited endpoint for testing."""
    return {"message": "This is an unlimited endpoint"}

@router.get("/limited")
@rate_limiter.limit("5/minute")
async def limited(request: Request):
    """Limited endpoint (5 requests per minute)."""
    return {
        "message": "This is a rate-limited endpoint (5 requests per minute)",
        "remaining": request.state.rate_limit_remaining,
        "reset": request.state.rate_limit_reset
    }

@router.get("/user-limited")
@rate_limiter.limit("10/minute", key_func=lambda r: f"user:{r.client.host}")
async def user_limited(request: Request):
    """User-specific rate limited endpoint (10 requests per minute per user)."""
    return {
        "message": "This is a user-specific rate-limited endpoint (10 requests per minute per user)",
        "remaining": request.state.rate_limit_remaining,
        "reset": request.state.rate_limit_reset
    }
