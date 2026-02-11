import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import core_router, get_auth_router
from app.core.config import settings
# if settings.code_intelligence_enabled:
#     from app.core.orchestration.queue_manager import AsyncQueueManager
#     from app.database.weaviate.client import get_weaviate_client
# DevRel commands are now loaded dynamically (commented out below)
# from integrations.discord.cogs import DevRelCommands

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DevRAIApplication:
    """
    Manages the application's core components and background tasks.
    """

    def __init__(self):
        """Initializes all services required by the application."""
        self.weaviate_client = None
        self.discord_bot = None
        self._discord_task = None
        self.agent_coordinator = None
        
        # Discord always exists if enabled
        if settings.discord_enabled:
            from integrations.discord.bot import DiscordBot
            from discord.ext import commands
            self.discord_bot = DiscordBot(queue_manager=None)
            self.queue_manager = None
        
        if settings.code_intelligence_enabled:
            from app.core.orchestration.queue_manager import AsyncQueueManager
            from app.database.weaviate.client import get_weaviate_client
            from app.core.orchestration.agent_coordinator import AgentCoordinator
            self.weaviate_client = get_weaviate_client()
            
            self.queue_manager = AsyncQueueManager()
            self.discord_bot= DiscordBot(self.queue_manager)
            self.agent_coordinator = AgentCoordinator(self.queue_manager)

    async def start_background_tasks(self):
        """
        Start all enabled background services including the Discord bot,
        queue workers, and code intelligence dependencies.
        """
        try:
            # Discord Mode
            if settings.discord_enabled:
                # 1. Start queue 
                if settings.code_intelligence_enabled:
                    await self.queue_manager.start(num_workers=3)

                # 2. Discord
                try:
                        await self.discord_bot.load_extension("integrations.discord.cogs")
                        self._discord_task = asyncio.create_task(
                            self.discord_bot.start(settings.discord_bot_token)
                        )
                except Exception as e:
                    logger.exception("Discord startup failed: %s",e)
                    self.discord_bot = None
            
            # Full Mode            
            if settings.code_intelligence_enabled:
                # Weaviate
                try:
                    await self.test_weaviate_connection()
                except Exception as e:
                    logger.warning("Weaviate disabled: %s", e)

                        
            logger.info(
            "Background services ready | queue=%s weaviate=%s discord=%s",
            bool(settings.rabbitmq_url),
            self.weaviate_client,
            bool(self.discord_bot),
            )        
            
        except Exception as e:
            logger.error(f"Error during background task startup: {e}", exc_info=True)
            await self.stop_background_tasks()
            raise

    async def test_weaviate_connection(self):
        """Test Weaviate connection during startup."""
        if not settings.code_intelligence_enabled:
            logger.info("Weaviate Is for Full Mode")
            return 
        try:
            from app.database.weaviate.client import get_weaviate_client
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
            if settings.discord_enabled and self.discord_bot and not self.discord_bot.is_closed():
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


api = FastAPI(title="Devr.AI API", version="1.0", lifespan=lifespan)

# Configure CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 logs"""
    return Response(status_code=204)

api.include_router(core_router)
if settings.github_enabled:
    api.include_router(get_auth_router())



if __name__ == "__main__":
    required_vars = [
        "BACKEND_URL"
    ]
    optional_vars = {
        "supabase": ["SUPABASE_URL", "SUPABASE_KEY"],
        "discord" : ["DISCORD_BOT_TOKEN"],
        "llm":["GEMINI_API_KEY"],
        "queue": ["RABBITMQ_URL"],  
        "search": ["TAVILY_API_KEY"],
        "github": ["GITHUB_TOKEN"]
    }
    missing_vars = [var for var in required_vars if not getattr(settings, var.lower(), None)]

    if missing_vars:
        raise RuntimeError(f"Core backend misconfigured. Missing: {','.join(missing_vars)} ")
    
    capabilities = {
    "discord_enabled": settings.discord_enabled,
    "llm_enabled": bool(settings.gemini_api_key),
    "github_enabled": settings.github_enabled,
    "code_intelligence": settings.code_intelligence_enabled,
    "search_enabled": bool(settings.tavily_api_key),
    "queue_enabled": bool(settings.rabbitmq_url),
    }
    
    if settings.code_intelligence_enabled:
        mode = "full"
    elif settings.github_enabled:
        mode = "discord+github"
    elif settings.discord_enabled:
        mode = "discord"
    else:
        mode = "minimal"

    logger.info(
        "Startup | mode=%s | capabilities=%s" ,
        mode,
        {k: v for k, v in capabilities.items() if v},
    )

    uvicorn.run(
        "__main__:api",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws_ping_interval=20,
        ws_ping_timeout=20
    )
