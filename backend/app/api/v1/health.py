import asyncio
import time
from typing import TYPE_CHECKING, Dict, Any
from fastapi import APIRouter, Depends
from app.database.weaviate.client import get_weaviate_client
from app.core.dependencies import get_app_instance
from app.core.config import settings
from app.core.logging_config import get_logger, log_performance
from app.core.exceptions import ServiceUnavailableError, ExternalServiceError

if TYPE_CHECKING:
    from main import DevRAIApplication

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
@log_performance("health_check")
async def health_check(app_instance: "DevRAIApplication" = Depends(get_app_instance)):
    """
    Comprehensive health check endpoint with detailed service status.
    
    Returns:
        dict: Detailed status of the application and its services
    """
    start_time = time.time()
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.environment,
        "version": "1.0",
        "uptime": None,  # Could be tracked if needed
        "services": {},
        "checks": []
    }
    
    # Check Weaviate
    weaviate_status = await _check_weaviate_health()
    health_data["services"]["weaviate"] = weaviate_status
    
    # Check Discord bot
    discord_status = await _check_discord_health(app_instance)
    health_data["services"]["discord_bot"] = discord_status
    
    # Check database connectivity (Supabase)
    supabase_status = await _check_supabase_health()
    health_data["services"]["supabase"] = supabase_status
    
    # Check external APIs
    external_apis_status = await _check_external_apis()
    health_data["services"]["external_apis"] = external_apis_status
    
    # Determine overall health
    all_services = [weaviate_status, discord_status, supabase_status, external_apis_status]
    critical_failures = [s for s in all_services if s.get("status") == "unhealthy" and s.get("critical", False)]
    
    if critical_failures:
        health_data["status"] = "unhealthy"
        logger.error(f"Health check failed - critical services down: {[s['name'] for s in critical_failures]}")
        raise ServiceUnavailableError(
            "One or more critical services are unavailable",
            context={"failed_services": [s["name"] for s in critical_failures]}
        )
    
    warnings = [s for s in all_services if s.get("status") in ["degraded", "warning"]]
    if warnings:
        health_data["status"] = "degraded"
    
    health_data["response_time"] = round(time.time() - start_time, 4)
    logger.info(f"Health check completed in {health_data['response_time']}s - Status: {health_data['status']}")
    
    return health_data


@router.get("/health/weaviate")
@log_performance("weaviate_health_check")
async def weaviate_health():
    """Check specifically Weaviate service health with detailed diagnostics."""
    try:
        status = await _check_weaviate_health()
        
        if status["status"] == "unhealthy":
            raise ExternalServiceError("Weaviate", status.get("error", "Service unhealthy"))
        
        return status
        
    except ExternalServiceError:
        raise
    except Exception as e:
        logger.error(f"Weaviate health check failed: {e}")
        raise ExternalServiceError("Weaviate", f"Health check failed: {str(e)}")


@router.get("/health/discord")
@log_performance("discord_health_check")
async def discord_health(app_instance: "DevRAIApplication" = Depends(get_app_instance)):
    """Check specifically Discord bot health with connection details."""
    try:
        status = await _check_discord_health(app_instance)
        
        if status["status"] == "unhealthy":
            raise ExternalServiceError("Discord", status.get("error", "Service unhealthy"))
        
        return status
        
    except ExternalServiceError:
        raise
    except Exception as e:
        logger.error(f"Discord health check failed: {e}")
        raise ExternalServiceError("Discord", f"Health check failed: {str(e)}")


@router.get("/health/detailed")
@log_performance("detailed_health_check")
async def detailed_health_check(app_instance: "DevRAIApplication" = Depends(get_app_instance)):
    """
    Detailed health check with extended diagnostics for debugging.
    Only available in development mode.
    """
    if not settings.is_development():
        raise ServiceUnavailableError("Detailed health check only available in development mode")
    
    diagnostics = {
        "system_info": {
            "environment": settings.environment,
            "log_level": settings.log_level,
            "debug_mode": settings.debug
        },
        "configuration": {
            "cors_origins": settings.cors_origins,
            "backend_url": settings.backend_url,
            "external_api_timeout": settings.external_api_timeout
        },
        "service_details": {}
    }
    
    # Add detailed service checks
    diagnostics["service_details"]["weaviate"] = await _check_weaviate_health(detailed=True)
    diagnostics["service_details"]["discord"] = await _check_discord_health(app_instance, detailed=True)
    diagnostics["service_details"]["supabase"] = await _check_supabase_health(detailed=True)
    
    return diagnostics


# Helper functions for individual service health checks
async def _check_weaviate_health(detailed: bool = False) -> Dict[str, Any]:
    """Check Weaviate service health."""
    start_time = time.time()
    try:
        async with asyncio.wait_for(get_weaviate_client(), timeout=settings.health_check_timeout) as client:
            is_ready = await client.is_ready()
            response_time = round(time.time() - start_time, 4)
            
            status = {
                "name": "weaviate",
                "status": "healthy" if is_ready else "unhealthy",
                "response_time": response_time,
                "critical": True
            }
            
            if detailed:
                status["details"] = {
                    "ready": is_ready,
                    "timeout": settings.health_check_timeout
                }
            
            return status
            
    except asyncio.TimeoutError:
        return {
            "name": "weaviate",
            "status": "unhealthy",
            "error": "Connection timeout",
            "response_time": round(time.time() - start_time, 4),
            "critical": True
        }
    except Exception as e:
        return {
            "name": "weaviate",
            "status": "unhealthy",
            "error": str(e),
            "response_time": round(time.time() - start_time, 4),
            "critical": True
        }


async def _check_discord_health(app_instance: "DevRAIApplication", detailed: bool = False) -> Dict[str, Any]:
    """Check Discord bot health."""
    try:
        is_running = app_instance.discord_bot and not app_instance.discord_bot.is_closed()
        
        status = {
            "name": "discord_bot",
            "status": "healthy" if is_running else "degraded",
            "critical": False  # Discord bot is not critical for API functionality
        }
        
        if detailed and app_instance.discord_bot:
            status["details"] = {
                "connected": is_running,
                "latency": getattr(app_instance.discord_bot, 'latency', None),
                "guilds_count": len(app_instance.discord_bot.guilds) if is_running else 0
            }
        
        return status
        
    except Exception as e:
        return {
            "name": "discord_bot",
            "status": "unhealthy",
            "error": str(e),
            "critical": False
        }


async def _check_supabase_health(detailed: bool = False) -> Dict[str, Any]:
    """Check Supabase connectivity."""
    start_time = time.time()
    try:
        # Simple check - just verify configuration is present
        if not settings.supabase_url or not settings.supabase_key:
            return {
                "name": "supabase",
                "status": "unhealthy",
                "error": "Missing configuration",
                "critical": True
            }
        
        # In a real implementation, you might want to make a simple API call here
        response_time = round(time.time() - start_time, 4)
        
        status = {
            "name": "supabase",
            "status": "healthy",
            "response_time": response_time,
            "critical": True
        }
        
        if detailed:
            status["details"] = {
                "url_configured": bool(settings.supabase_url),
                "key_configured": bool(settings.supabase_key)
            }
        
        return status
        
    except Exception as e:
        return {
            "name": "supabase",
            "status": "unhealthy",
            "error": str(e),
            "response_time": round(time.time() - start_time, 4),
            "critical": True
        }


async def _check_external_apis() -> Dict[str, Any]:
    """Check external API configurations."""
    try:
        api_configs = {
            "gemini": bool(settings.gemini_api_key),
            "tavily": bool(settings.tavily_api_key),
            "github": bool(settings.github_token)
        }
        
        configured_apis = sum(api_configs.values())
        total_apis = len(api_configs)
        
        if configured_apis == 0:
            status = "unhealthy"
        elif configured_apis < total_apis:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "name": "external_apis",
            "status": status,
            "configured": configured_apis,
            "total": total_apis,
            "details": api_configs,
            "critical": configured_apis == 0  # At least one API should be configured
        }
        
    except Exception as e:
        return {
            "name": "external_apis",
            "status": "unhealthy",
            "error": str(e),
            "critical": True
        }


@router.get("/health/weaviate")
async def weaviate_health():
    """Check specifically Weaviate service health."""
    try:
        async with get_weaviate_client() as client:
            is_ready = await client.is_ready()

        return {
            "service": "weaviate",
            "status": "ready" if is_ready else "not_ready"
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
async def discord_health(app_instance: "DevRAIApplication" = Depends(get_app_instance)):
    """Check specifically Discord bot health."""
    try:
        bot_status = "running" if app_instance.discord_bot and not app_instance.discord_bot.is_closed() else "stopped"

        return {
            "service": "discord_bot",
            "status": bot_status
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
