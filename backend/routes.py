import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header
from app.core.events.event_bus import EventBus
from app.core.events.enums import EventType, PlatformType
from app.core.events.base import BaseEvent
from app.core.handler.handler_registry import HandlerRegistry
from pydantic import BaseModel
from app.core.config.settings import settings

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

async def verify_signature(request: Request, x_hub_signature_256: str = Header(None)):
    """Verify that the payload was sent from GitHub by validating the SHA256 signature."""
    if not settings.github_webhook_secret:
        # If secret is not configured, we skip verification (not recommended for production)
        return

    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="X-Hub-Signature-256 header is missing")

    body = await request.body()
    signature = hmac.new(
        settings.github_webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={signature}", x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

@router.post("/github/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    # Verify GitHub signature
    await verify_signature(request, x_hub_signature_256)

    payload = await request.json()
    logging.info(f"Received GitHub event: {x_github_event}")

    event_type = None

    # Mapping GitHub events and actions to EventType
    event_mapping = {
        "issues": {
            "opened": EventType.ISSUE_CREATED,
            "closed": EventType.ISSUE_CLOSED,
            "edited": EventType.ISSUE_UPDATED,
        },
        "issue_comment": {
            "created": EventType.ISSUE_COMMENTED,
        },
        "pull_request": {
            "opened": EventType.PR_CREATED,
            "edited": EventType.PR_UPDATED,
        },
        "pull_request_review_comment": {
            "created": EventType.PR_COMMENTED,
        },
        "pull_request_comment": {
            "created": EventType.PR_COMMENTED,
        }
    }

    if x_github_event in event_mapping:
        action = payload.get("action")
        event_type = event_mapping[x_github_event].get(action)

        # Special casing for PR merged
        if x_github_event == "pull_request" and action == "closed":
            if payload.get("pull_request", {}).get("merged"):
                event_type = EventType.PR_MERGED
            else:
                logging.info("Pull request closed without merge; no event dispatched.")

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
        logging.info(f"No matching event type for header: {x_github_event} with action: {payload.get('action')}")

    return {"status": "ok"}
