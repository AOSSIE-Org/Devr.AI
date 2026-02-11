from fastapi import APIRouter
from .v1.health import router as health_router

core_router = APIRouter()
# -------- Core Router ---------------
core_router.include_router(
    health_router,
    prefix="/v1",
    tags=["Health"]
)

# -------- Auth router --------
def get_auth_router() -> APIRouter:
    router= APIRouter()
    from .v1.auth import router as auth_router
    from .v1.integrations import router as integrations_router
    router.include_router(
        auth_router,
        prefix="/v1/auth",
        tags=["Authentication"]
    )

    router.include_router(
        integrations_router,
        prefix="/v1/integrations",
        tags=["Integrations"]
    )
    
    return router

__all__ = ["core_router", "get_auth_router"]
