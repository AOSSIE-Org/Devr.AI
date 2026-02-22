from app.services.github.issue_suggestion_service import IssueSuggestionService
from app.core.config import settings

import uuid
import logging
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException
from app.core.events.event_bus import EventBus
from app.core.events.enums import EventType, PlatformType
from app.core.events.base import BaseEvent
from app.core.handler.handler_registry import HandlerRegistry
from pydantic import BaseModel

router = APIRouter()

logger = logging.getLogger(__name__)

handler_registry = HandlerRegistry()
event_bus = EventBus(handler_registry)


class RepoRequest(BaseModel):
    repo_url: str


# ---------------------------------------------------------
# Sample Event Handler
# ---------------------------------------------------------

async def sample_handler(event: BaseEvent):
    logger.info(
        f"Handler received event: {event.event_type} with data: {event.raw_data}"
    )


# ---------------------------------------------------------
# Register Event Handlers
# ---------------------------------------------------------

def register_event_handlers():
    event_bus.register_handler(EventType.ISSUE_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_CLOSED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_UPDATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.ISSUE_COMMENTED, sample_handler, PlatformType.GITHUB)

    event_bus.register_handler(EventType.PR_CREATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_UPDATED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_COMMENTED, sample_handler, PlatformType.GITHUB)
    event_bus.register_handler(EventType.PR_MERGED, sample_handler, PlatformType.GITHUB)


# ---------------------------------------------------------
# GitHub Webhook Endpoint (SECURE VERSION)
# ---------------------------------------------------------

@router.post("/github/webhook")
async def github_webhook(request: Request):

    # 🔐 Signature Verification
    webhook_secret = settings.github_token_resolved  # Replace with dedicated webhook secret if available
    signature_header = request.headers.get("X-Hub-Signature-256")

    body = await request.body()

    if not signature_header:
        raise HTTPException(status_code=400, detail="Missing signature")

    sha_name, signature = signature_header.split("=")

    if sha_name != "sha256":
        raise HTTPException(status_code=400, detail="Invalid signature format")

    mac = hmac.new(
        webhook_secret.encode(),
        msg=body,
        digestmod=hashlib.sha256
    )

    expected_signature = mac.hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    event_header = request.headers.get("X-GitHub-Event")

    logger.info(f"Received GitHub event: {event_header}")

    event_type = None

    if event_header == "issues":
        action = payload.get("action")
        if action == "opened":
            event_type = EventType.ISSUE_CREATED
        elif action == "closed":
            event_type = EventType.ISSUE_CLOSED
        elif action == "edited":
            event_type = EventType.ISSUE_UPDATED

    elif event_header == "issue_comment":
        if payload.get("action") == "created":
            event_type = EventType.ISSUE_COMMENTED

    elif event_header == "pull_request":
        action = payload.get("action")

        if action == "opened":
            event_type = EventType.PR_CREATED
        elif action == "edited":
            event_type = EventType.PR_UPDATED
        elif action == "closed" and payload.get("pull_request", {}).get("merged"):
            event_type = EventType.PR_MERGED

    elif event_header in ["pull_request_review_comment", "pull_request_comment"]:
        if payload.get("action") == "created":
            event_type = EventType.PR_COMMENTED

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
        logger.info(
            f"No matching event type for header: {event_header} with action: {payload.get('action')}"
        )

    return {"status": "ok"}


# ---------------------------------------------------------
# Beginner Issues Endpoint (FIXED & CONSISTENT)
# ---------------------------------------------------------

@router.get("/beginner-issues")
async def get_beginner_issues(
    language: str = "python",
    limit: int = 5
):
    """
    Fetch global beginner-friendly GitHub issues.
    """

    token = settings.github_token_resolved

    if not token:
        raise HTTPException(
            status_code=500,
            detail="GitHub token not configured"
        )

    issue_service = IssueSuggestionService(token)

    try:
        issues = await issue_service.fetch_beginner_issues(
            language=language,
            limit=limit
        )

        return {
            "language": language,
            "count": len(issues),
            "issues": issues
        }

    except Exception as e:
        logger.error(f"Error fetching beginner issues: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch beginner issues"
        ) from e