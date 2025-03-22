import asyncio
import uuid
import logging
from fastapi import APIRouter, Request, HTTPException
from app.core.events.event_bus import EventBus
from app.core.events.enums import EventType, PlatformType
from app.core.events.base import BaseEvent
from app.core.handler.handler_registry import HandlerRegistry
from pydantic import BaseModel

router = APIRouter()

class RepoRequest(BaseModel):
    repo_url: str

logging.basicConfig(level=logging.INFO)
handler_registry = HandlerRegistry()
event_bus = EventBus(handler_registry)

# Sample handler function to process events
async def sample_handler(event: BaseEvent):
    logging.info(f"Handler received event: {event.event_type} with data: {event.raw_data}")

# Register all the event handlers for issues and pull requests
def register_event_handlers():
    # Issue events
    event_bus.register_handler(EventType.ISSUE_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_CLOSED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_UPDATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_COMMENTED, sample_handler, PlatformType.GITHUB)
    # Pull request events
    event_bus.register_handler(EventType.PR_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_UPDATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_COMMENTED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_MERGED, sample_handler, PlatformType.GITHUB)

@router.post("/github/webhook")
async def github_webhook(request: Request):
    payload = await request.json()
    event_header = request.headers.get("X-GitHub-Event")
    logging.info(f"Received GitHub event: {event_header}")

    event_type = None

    # Handle issue events
    if event_header == "issues":
        action = payload.get("action")
        if action == "opened":
            event_type = EventType.ISSUE_CREATED
        elif action == "closed":
            event_type = EventType.ISSUE_CLOSED
        elif action == "edited":
            event_type = EventType.ISSUE_UPDATED

    # Handle issue comment events
    elif event_header == "issue_comment":
        action = payload.get("action")
        if action == "created":
            event_type = EventType.ISSUE_COMMENTED

    # Handle pull request events
    elif event_header == "pull_request":
        action = payload.get("action")
        if action == "opened":
            event_type = EventType.PR_CREATED
        elif action == "edited":
            event_type = EventType.PR_UPDATED
        elif action == "closed":
            # Determine if the PR was merged or simply closed
            if payload.get("pull_request", {}).get("merged"):
                event_type = EventType.PR_MERGED
            else:
                logging.info("Pull request closed without merge; no event dispatched.")
    
    # Handle pull request comment events
    elif event_header in ["pull_request_review_comment", "pull_request_comment"]:
        action = payload.get("action")
        if action == "created":
            event_type = EventType.PR_COMMENTED

    # Dispatch the event if we have a matching type
    if event_type:
        event = BaseEvent(
            id=str(uuid.uuid4()),
            actor_id=str(payload.get("sender", {}).get("id", "unknown")),
            event_type=event_type,
            platform=PlatformType.GITHUB,
            raw_data=payload
        )
        await event_bus.dispatch(event)
    else:
        logging.info(f"No matching event type for header: {event_header} with action: {payload.get('action')}")

    return {"status": "ok"}
