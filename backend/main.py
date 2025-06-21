import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Response

from app.api.v1.auth import router as auth_router
from app.core.config import settings
from app.core.orchestration.agent_coordinator import AgentCoordinator
from app.core.orchestration.queue_manager import AsyncQueueManager
# from app.db.weaviate.weaviate_client import get_client
from bots.discord.discord_bot import DiscordBot
from bots.discord.discord_cogs import DevRelCommands

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
        # try:
        #     self.weaviate_client = get_client()
        #     logger.info(f"Weaviate client initialized: {self.weaviate_client.is_ready()}")
        # except Exception as e:
        #     logger.error(f"Fatal: Error initializing Weaviate client: {e}", exc_info=True)
        #     self.weaviate_client = None
        #     sys.exit(1)
        self.queue_manager = AsyncQueueManager()
        self.agent_coordinator = AgentCoordinator(self.queue_manager)
        self.discord_bot = DiscordBot(self.queue_manager)
        self.discord_bot.add_cog(DevRelCommands(self.discord_bot, self.queue_manager))

    async def start_background_tasks(self):
        """Starts the Discord bot and queue workers in the background."""
        try:
            logger.info("Starting background tasks (Discord Bot & Queue Manager)...")
            await self.queue_manager.start(num_workers=3)
            asyncio.create_task(
                self.discord_bot.start(settings.discord_bot_token)
            )
            logger.info("Background tasks started successfully!")
        except Exception as e:
            logger.error(f"Error during background task startup: {e}", exc_info=True)
            await self.stop_background_tasks()

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

        try:
            if hasattr(self, 'weaviate_client') and self.weaviate_client is not None:
                self.weaviate_client.close()
                logger.info("Weaviate client connection closed.")
        except Exception as e:
            logger.error(f"Error closing Weaviate client: {e}", exc_info=True)

        logger.info("All background tasks and connections stopped.")


# --- FASTAPI LIFESPAN AND APP INITIALIZATION ---
# Global application instance
app_instance = DevRAIApplication()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for the FastAPI application. Handles startup and shutdown events.
    """
    await app_instance.start_background_tasks()
    yield
    await app_instance.stop_background_tasks()


api = FastAPI(title="Devr.AI API", version="1.0", lifespan=lifespan)

@api.get("/favicon.ico")
async def favicon():
    """Return empty favicon to prevent 404 logs"""
    return Response(status_code=204)

api.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])


if __name__ == "__main__":
    required_vars = [
        "DISCORD_BOT_TOKEN", "SUPABASE_URL", "SUPABASE_KEY",
        "BACKEND_URL", "GEMINI_API_KEY", "TAVILY_API_KEY"
    ]
    missing_vars = [var for var in required_vars if not getattr(settings, var.lower(), None)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    uvicorn.run(
        "__main__:api",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
