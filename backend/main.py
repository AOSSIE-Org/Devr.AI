
from fastapi import FastAPI
from app.db.db import engine
from app.models import models
from app.routes.post import router as post_router
from sqlalchemy.exc import SQLAlchemyError
# import logging
# import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Async function to create database tables with exception handling
async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        print("✅ Tables created successfully or already exist.")
    except SQLAlchemyError as e:
        print(f"❌ Error creating tables: {e}")

#Lifespan context manager for startup and shutdown events

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting...")
    await create_tables()
    yield
    print("App is shutting down...")

# Initialize FastAPI
app = FastAPI(lifespan=lifespan)

# Include the routes
app.include_router(post_router)

@app.get("/")
async def home():
    try:
        return {"message": "Welcome to Inpact API!"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

import asyncio
import uuid
import logging
from .app.core.events.event_bus import EventBus
from .app.core.events.enums import EventType, PlatformType
from .app.core.events.base import BaseEvent
from .app.core.handler.handler_registry import HandlerRegistry

logging.basicConfig(level=logging.INFO)

# Initialize Handler Registry and Event Bus
handler_registry = HandlerRegistry()
event_bus = EventBus(handler_registry)

# Sample Handler Function
async def sample_handler(event: BaseEvent):
    logging.info(f"Handler received event: {event.event_type} with data: {event.raw_data}")

# Register Handlers
def register_event_handlers():
    event_bus.register_handler(EventType.ISSUE_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_COMMENTED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ONBOARDING_COMPLETED, sample_handler, PlatformType.DISCORD)

# Create a test event
def create_test_event(event_type: EventType, platform: PlatformType, raw_data: dict) -> BaseEvent:
    return BaseEvent(
        id=str(uuid.uuid4()),
        actor_id="1234",
        event_type=event_type,
        platform=platform,
        raw_data=raw_data
    )

# Test Event Dispatching
async def test_event_dispatch(event_type: EventType, platform: PlatformType, raw_data: dict):
    event = create_test_event(event_type, platform, raw_data)
    await event_bus.dispatch(event)

# Main function to run all tests
async def main():
    logging.info("Starting EventBus Tests...")
    register_event_handlers()

    test_cases = [
        (EventType.ISSUE_CREATED, PlatformType.GITHUB, {"title": "Bug Report", "description": "Issue in production"}),
        (EventType.PR_COMMENTED, PlatformType.GITHUB, {"pr_id": 5678, "merged_by": "dev_user"}),
        (EventType.ONBOARDING_COMPLETED, PlatformType.DISCORD, {"channel": "general", "content": "Hello everyone!"})
    ]

    for event_type, platform, data in test_cases:
        await test_event_dispatch(event_type, platform, data)

    logging.info("All EventBus Tests Completed.")

if __name__ == "__main__":
    asyncio.run(main())

