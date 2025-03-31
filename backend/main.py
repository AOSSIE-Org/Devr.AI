import asyncio
import uuid
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure absolute imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.events.event_bus import EventBus
from backend.app.core.events.enums import EventType, PlatformType
from backend.app.core.events.base import BaseEvent
from backend.app.core.handler.handler_registry import HandlerRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Devr.AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {"message": "Welcome to Devr.AI API"}

@app.get("/test")
async def test_endpoint():
    # Create and dispatch a test event
    event = create_test_event(
        EventType.ISSUE_CREATED, 
        PlatformType.GITHUB, 
        {"title": "Test Event", "description": "This is a test"}
    )
    await event_bus.dispatch(event)
    return {"message": "Test event dispatched", "event_id": event.id}

if __name__ == "__main__":
    # Register event handlers
    register_event_handlers()
    
    # Start the FastAPI server
    logger.info("Starting Devr.AI backend server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)