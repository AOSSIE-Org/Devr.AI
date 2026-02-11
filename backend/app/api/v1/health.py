import logging
from fastapi import APIRouter, HTTPException, Request
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

async def get_weaviate_status() -> str:
    if not settings.code_intelligence_enabled:
        return "disabled"

    from app.database.weaviate.client import get_weaviate_client
    async with get_weaviate_client() as client:
        return "ready" if await client.is_ready() else "not_ready"


def get_discord_status(app_instance) -> str:
    if not settings.discord_enabled:
        return "disabled"

    bot = app_instance.discord_bot
    return "running" if bot and not bot.is_closed() else "stopped"

@router.get("/health")
async def health_check(request: Request):
    """
    General health check endpoint to verify services are running.

    Returns:
        dict: Status of the application and its services
    """
    try:
        services = {
            "weaviate": await get_weaviate_status(),
            "discord": get_discord_status(request.app.state.app_instance),
        }
 
        return {
            "status": "healthy",
            "services": services,
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        ) from e


@router.get("/health/weaviate")
async def weaviate_health():
    """Check specifically Weaviate service health."""
    try:
        return {
            "service": "weaviate",
            "status": await get_weaviate_status(),
            }
    
    except Exception as e:
        logger.error(f"Weaviate health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "service": "weaviate",
                "status": "unhealthy",
                "error": str(e)
            }
        ) from e


@router.get("/health/discord")
async def discord_health(request: Request):
    """Check specifically Discord bot health."""
    try:
        return {
            "service": "discord_bot",
            "status": get_discord_status(request.app.state.app_instance),
        }
    
    except Exception as e:
        logger.error(f"Discord bot health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "service": "discord_bot",
                "status": "unhealthy",
                "error": str(e)
            }
        ) from e
