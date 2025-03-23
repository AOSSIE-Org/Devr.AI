
import asyncio
import uuid
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router  
import uvicorn
from .app.core.events.event_bus import EventBus
from .app.core.events.enums import EventType, PlatformType
from .app.core.events.base import BaseEvent
from .app.core.handler.handler_registry import HandlerRegistry

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  
)

app.include_router(router, prefix="/api")  

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
    uvicorn.run(app, host="127.0.0.1", port=8000)
    asyncio.run(main())

