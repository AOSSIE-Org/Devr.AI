"""
CORS (Cross-Origin Resource Sharing) middleware with security policies.
Configures allowed origins, methods, and headers for API security.
"""
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_cors_config():
    """
    Get CORS configuration based on environment.
    
    Returns:
        Dictionary with CORS settings
    """
    # Production origins (whitelist specific domains)
    production_origins = [
        "https://devr.ai",
        "https://www.devr.ai",
        "https://app.devr.ai",
    ]
    
    # Development origins
    development_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    
    # Determine if in production
    is_production = getattr(settings, 'environment', 'development') == 'production'
    
    if is_production:
        allowed_origins = production_origins
        logger.info("CORS configured for production environment")
    else:
        allowed_origins = production_origins + development_origins
        logger.info("CORS configured for development environment")
    
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Requested-With",
            "X-CSRF-Token",
        ],
        "expose_headers": [
            "Content-Length",
            "X-RateLimit-Limit-Minute",
            "X-RateLimit-Remaining-Minute",
            "X-RateLimit-Limit-Hour",
            "X-RateLimit-Remaining-Hour",
        ],
        "max_age": 600,  # Cache preflight requests for 10 minutes
    }


def setup_cors(app):
    """
    Setup CORS middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    cors_config = get_cors_config()
    
    app.add_middleware(
        CORSMiddleware,
        **cors_config
    )
    
    logger.info(f"CORS middleware configured with {len(cors_config['allow_origins'])} allowed origins")
