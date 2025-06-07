import asyncio
import logging
import os
import signal
from app.core.config import settings
from app.core.orchestration.queue_manager import AsyncQueueManager
from app.core.orchestration.agent_coordinator import AgentCoordinator
from bots.discord.discord_bot import DiscordBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DevRAIApplication:
    """Main application class"""

    def __init__(self):
        self.queue_manager = AsyncQueueManager()
        self.agent_coordinator = AgentCoordinator(self.queue_manager)
        self.discord_bot = DiscordBot(self.queue_manager)
        self.running = False

    async def start(self):
        """Start the application"""
        try:
            logger.info("Starting Devr.AI Application...")

            # Start queue manager
            await self.queue_manager.start(num_workers=3)

            # Start Discord bot
            discord_task = asyncio.create_task(
                self.discord_bot.start(settings.discord_bot_token)
            )

            self.running = True
            logger.info("Devr.AI Application started successfully!")

            # Wait for the Discord bot
            await discord_task

        except Exception as e:
            logger.error(f"Error starting application: {str(e)}")
            await self.stop()

    async def stop(self):
        """Stop the application"""
        logger.info("Stopping Devr.AI Application...")

        self.running = False

        # Stop Discord bot
        if not self.discord_bot.is_closed():
            await self.discord_bot.close()

        # Stop queue manager
        await self.queue_manager.stop()

        logger.info("Devr.AI Application stopped")


# Global application instance
app = DevRAIApplication()

async def main():
    """Main entry point"""

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()

    def signal_handler(signum):
        logger.info(f"Received signal {signum}")
        loop.create_task(app.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: signal_handler(s), sig)

    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        await app.stop()

if __name__ == "__main__":
    # Check required environment variables
    required_vars = ["DISCORD_BOT_TOKEN", "GEMINI_API_KEY", "TAVILY_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        exit(1)

    # Run the application
    asyncio.run(main())
