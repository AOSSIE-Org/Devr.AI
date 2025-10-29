import asyncio
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.middleware import ErrorHandlingMiddleware, setup_error_handlers
from app.core.orchestration.agent_coordinator import AgentCoordinator
from app.core.orchestration.queue_manager import AsyncQueueManager
from app.database.weaviate.client import get_weaviate_client
from integrations.discord.bot import DiscordBot
from discord.ext import commands

# Setup logging first
setup_logging()
logger = get_logger(__name__)


class DevRAIApplication:
    """
    Manages the application's core components and background tasks.
    """

    def __init__(self):
        """Initializes all services required by the application."""
        self.weaviate_client = None
        self.queue_manager = AsyncQueueManager()
        self.agent_coordinator = AgentCoordinator(self.queue_manager)
        self.discord_bot = DiscordBot(self.queue_manager)

    async def start_background_tasks(self):
        """Starts the Discord bot and queue workers in the background."""
        try:
            logger.info("Starting background tasks (Discord Bot & Queue Manager)...")

            await self.test_weaviate_connection()

            await self.queue_manager.start(num_workers=3)

            # --- Load commands inside the async startup function ---
            try:
                await self.discord_bot.load_extension("integrations.discord.cogs")
            except (ImportError, commands.ExtensionError) as e:
                logger.error("Failed to load Discord cog extension: %s", e)

            # Start the bot as a background task.
            asyncio.create_task(
                self.discord_bot.start(settings.discord_bot_token)
            )
            logger.info("Background tasks started successfully!")
        except Exception as e:
            logger.error(f"Error during background task startup: {e}", exc_info=True)
            await self.stop_background_tasks()
            raise

    async def test_weaviate_connection(self):
        """Test Weaviate connection during startup."""
        try:
            async with get_weaviate_client() as client:
                if await client.is_ready():
                    logger.info("Weaviate connection successful and ready")
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise

    async def stop_background_tasks(self):
        """Stops all background tasks and connections gracefully."""
        logger.info("Stopping background tasks and closing connections...")
        try:
            if not self.discord_bot.is_closed():
                await self.discord_bot.close()
                logger.info("Discord bot has been closed.")
        except Exception as e:
            logger.error(f"Error closing Discord bot: {e}", exc_info=True)
        try:
            await self.queue_manager.stop()
            logger.info("Queue manager has been stopped.")
        except Exception as e:
            logger.error(f"Error stopping queue manager: {e}", exc_info=True)
        logger.info("All background tasks and connections stopped.")


# --- FASTAPI LIFESPAN AND APP INITIALIZATION ---
app_instance = DevRAIApplication()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for the FastAPI application. Handles startup and shutdown events.
    """
    app.state.app_instance = app_instance
    await app_instance.start_background_tasks()
    yield
    await app_instance.stop_background_tasks()


api = FastAPI(
    title="Devr.AI API", 
    version="1.0", 
    lifespan=lifespan,
    description="AI-powered Developer Relations platform",
    docs_url="/docs" if settings.is_development() else None,
    redoc_url="/redoc" if settings.is_development() else None
)

# Add error handling middleware
api.add_middleware(ErrorHandlingMiddleware)

# Configure CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Process-Time"]
)

# Setup error handlers
setup_error_handlers(api)

@api.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 logs"""
    return Response(status_code=204)

api.include_router(api_router)


if __name__ == "__main__":
    try:
        # Validate configuration
        missing_services = settings.validate_required_services()
        if missing_services and settings.is_production():
            logger.error(f"Missing required services in production: {', '.join(missing_services)}")
            sys.exit(1)
        elif missing_services:
            logger.warning(f"Missing optional services: {', '.join(missing_services)}")
        
        logger.info(f"Starting Devr.AI API in {settings.environment} mode")
        logger.info(f"Log level set to: {settings.log_level}")
        
        # Configure uvicorn settings based on environment
        uvicorn_config = {
            "app": "__main__:api",
            "host": "0.0.0.0",
            "port": 8000,
            "ws_ping_interval": 20,
            "ws_ping_timeout": 20,
            "access_log": True,
            "log_level": settings.log_level.lower()
        }
        
        # Enable reload only in development
        if settings.is_development():
            uvicorn_config["reload"] = True
            uvicorn_config["debug"] = settings.debug
        
        uvicorn.run(**uvicorn_config)
        
    except KeyboardInterrupt:
        logger.info("Application shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)
