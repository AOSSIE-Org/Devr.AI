import asyncio
import uuid
import logging
from .app.core.events.event_bus import EventBus
from .app.core.events.enums import EventType, PlatformType
from .app.core.events.base import BaseEvent
from .app.core.handler.handler_registry import HandlerRegistry

# Enhanced logging configuration with timestamp and file logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("eventbus.log"),
        logging.StreamHandler()
    ]
)

# Initialize Handler Registry and Event Bus
handler_registry = HandlerRegistry()
event_bus = EventBus(handler_registry)

# Sample Handler Function with optional error simulation for testing
async def sample_handler(event: BaseEvent):
    logging.info(f"Handler received event: {event.event_type} with data: {event.raw_data}")
    # Uncomment the next two lines to simulate an error for testing error handling:
    # if "simulate_error" in event.raw_data:
    #     raise ValueError("Simulated error in sample_handler!")

# Register Handlers for specific event types and platforms
def register_event_handlers():
    event_bus.register_handler(EventType.ISSUE_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_COMMENTED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ONBOARDING_COMPLETED, sample_handler, PlatformType.DISCORD)

# Create a test event with a unique identifier and provided data
def create_test_event(event_type: EventType, platform: PlatformType, raw_data: dict) -> BaseEvent:
    return BaseEvent(
        id=str(uuid.uuid4()),
        actor_id="1234",
        event_type=event_type,
        platform=platform,
        raw_data=raw_data
    )

# Test Event Dispatching with error handling to capture any exceptions during dispatch
async def test_event_dispatch(event_type: EventType, platform: PlatformType, raw_data: dict):
    try:
        event = create_test_event(event_type, platform, raw_data)
        await event_bus.dispatch(event)
    except Exception as e:
        logging.exception(f"Error dispatching event {event_type.name} for platform {platform.name}")

# Main function to run all tests
async def main():
    logging.info("Starting EventBus Tests...")
    register_event_handlers()

    test_cases = [
        (EventType.ISSUE_CREATED, PlatformType.GITHUB, {"title": "Bug Report", "description": "Issue in production"}),
        (EventType.PR_COMMENTED, PlatformType.GITHUB, {"pr_id": 5678, "merged_by": "dev_user"}),
        (EventType.ONBOARDING_COMPLETED, PlatformType.DISCORD, {"channel": "general", "content": "Hello everyone!"}),
        # Uncomment to simulate an error in the handler:
        # (EventType.ISSUE_CREATED, PlatformType.GITHUB, {"simulate_error": True})
    ]

    for event_type, platform, data in test_cases:
        await test_event_dispatch(event_type, platform, data)

    logging.info("All EventBus Tests Completed.")

# Global exception handler to catch unhandled exceptions in the main loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Unhandled exception occurred in EventBus test runner.")
