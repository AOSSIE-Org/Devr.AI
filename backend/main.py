import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from integrations.discord.bot import DiscordBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DevRAIApplication:
    """
    DEV MODE - Only Discord bot.
    No Queue. No Agent. No Gemini. No Weaviate.
    """

    def __init__(self):
        self.discord_bot = DiscordBot()

    async def start_background_tasks(self):
        logger.info("Starting Discord bot (DEV MODE)...")

        asyncio.create_task(
            self.discord_bot.start(settings.discord_bot_token)
        )

        logger.info("Discord bot started successfully!")

    async def stop_background_tasks(self):
        logger.info("Stopping Discord bot...")
        try:
            if not self.discord_bot.is_closed():
                await self.discord_bot.close()
        except Exception as e:
            logger.error(f"Error closing Discord bot: {e}")


# --- FASTAPI LIFESPAN ---
app_instance = DevRAIApplication()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_instance.start_background_tasks()
    yield
    await app_instance.stop_background_tasks()


api = FastAPI(title="Devr.AI API", version="1.0", lifespan=lifespan)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


api.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "__main__:api",
        host="0.0.0.0",
        port=8000,
        reload=True
    )