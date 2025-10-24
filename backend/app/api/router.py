from fastapi import APIRouter
from .v1.auth import router as auth_router
from .v1.health import router as health_router
from .v1.integrations import router as integrations_router

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/v1/auth",
    tags=["Authentication"]
)

api_router.include_router(
    health_router,
    prefix="/v1",
    tags=["Health"]
)

api_router.include_router(
    integrations_router,
    prefix="/v1/integrations",
    tags=["Integrations"]
)

__all__ = ["api_router"]
