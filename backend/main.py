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

# Slack-specific handler
async def slack_handler(event: BaseEvent):
    logging.info(f"Slack Event: {event.event_type}, Channel: {event.raw_data.get('channel_id')}, Message: {event.raw_data.get('message')}")

# Register Handlers
def register_event_handlers():
    event_bus.register_handler(EventType.ISSUE_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_COMMENTED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ONBOARDING_COMPLETED, sample_handler, PlatformType.DISCORD)
    
    # Slack-specific event handlers
    event_bus.register_handler(EventType.MESSAGE_RECEIVED, slack_handler, PlatformType.SLACK)
    event_bus.register_handler(EventType.USER_MENTIONED, slack_handler, PlatformType.SLACK)

# Create a test event
def create_test_event(event_type: EventType, platform: PlatformType, raw_data: dict) -> BaseEvent:
    return BaseEvent(
        id=str(uuid.uuid4()),
        actor_id="1234",
        event_type=event_type,
        platform=platform,
        raw_data=raw_data
    )

# Slack-specific event creation helper
def create_slack_event(event_type: EventType, channel_id: str, message: str, user_id: str = None) -> BaseEvent:
    """
    Helper function to create Slack-specific events
    
    Args:
        event_type (EventType): Type of Slack event
        channel_id (str): Slack channel ID
        message (str): Message content
        user_id (str, optional): ID of the user who sent the message
    
    Returns:
        BaseEvent: Slack event
    """
    return BaseEvent(
        id=str(uuid.uuid4()),
        actor_id=user_id or "unknown",
        event_type=event_type,
        platform=PlatformType.SLACK,
        raw_data={
            "channel_id": channel_id,
            "message": message,
            "timestamp": str(uuid.uuid1())  # Adding timestamp for tracking
        }
    )

# Test Event Dispatching
async def test_event_dispatch(event_type: EventType, platform: PlatformType, raw_data: dict):
    event = create_test_event(event_type, platform, raw_data)
    await event_bus.dispatch(event)

# Main function to run all tests and keep the server alive
async def main():
    logging.info("Starting EventBus Tests...")
    register_event_handlers()

    test_cases = [
        (EventType.ISSUE_CREATED, PlatformType.GITHUB, {"title": "Bug Report", "description": "Issue in production"}),
        (EventType.PR_COMMENTED, PlatformType.GITHUB, {"pr_id": 5678, "merged_by": "dev_user"}),
        (EventType.ONBOARDING_COMPLETED, PlatformType.DISCORD, {"channel": "general", "content": "Hello everyone!"}),
        
        # Slack test cases
        (EventType.MESSAGE_RECEIVED, PlatformType.SLACK, {"channel_id": "C07NR9A9V8U", "message": "Hello from Slack!"}),
        (EventType.USER_MENTIONED, PlatformType.SLACK, {"user_id": "D07NR9A8E5S", "message": "@Slackbot"})
    ]

    # Slack-specific test events
    slack_test_events = [
        create_slack_event(
            EventType.MESSAGE_RECEIVED, 
            channel_id="C07NR9A9V8U", 
            message="Test Slack message", 
            user_id="U789"
        ),
        create_slack_event(
            EventType.USER_MENTIONED, 
            channel_id="C07NR9A9V8U", 
            message="@DevrAIBot Hello!", 
            user_id="U101"
        )
    ]

    # Dispatch original test cases
    for event_type, platform, data in test_cases:
        await test_event_dispatch(event_type, platform, data)
    
    # Dispatch Slack-specific test events
    for event in slack_test_events:
        await event_bus.dispatch(event)

    logging.info("All EventBus Tests Completed.")
    
    # Keep the event loop running indefinitely
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
