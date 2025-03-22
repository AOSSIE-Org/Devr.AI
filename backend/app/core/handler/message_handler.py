import logging
from typing import Dict, Any
from ..events.base import BaseEvent
from ..events.enums import EventType
from .base import BaseHandler
from .faq_handler import FAQHandler
logger = logging.getLogger(__name__)

class MessageHandler(BaseHandler):
    """Handler for Discord/Slack message events"""

    def __init__(self, bot=None):
        self.bot = bot
        self.faq_handler = FAQHandler()

    async def handle(self, event: BaseEvent) -> Dict[str, Any]:
        logger.info(f"Handling message event from {event.platform}: {event.event_type}")
        if event.event_type == EventType.MESSAGE_CREATED:
            return await self._handle_message_created(event)
        elif event.event_type == EventType.MESSAGE_UPDATED:
            return await self._handle_message_updated(event)
        else:
            logger.warning(f"Unsupported message event type: {event.event_type}")
            return {"success": False, "reason": "Unsupported event type"}

    async def _handle_message_created(self, event: BaseEvent) -> Dict[str, Any]:

        user_message = (event.content or "").strip().lower()

        if not user_message:
            logger.error(f"Received empty message event: {event}")
            return {"success": False, "reason": "Empty message"}

        # Check if it's a FAQ request
        if await self.faq_handler.is_faq(user_message):
            faq_event = BaseEvent(
                id=event.id,
                event_type=EventType.FAQ_REQUESTED,
                platform=event.platform,
                channel_id=event.raw_data.get("channel_id"),
                actor_id=event.actor_id,
                data={"content": user_message},
            )
            return await self.faq_handler.handle(faq_event)

        # Implementation for new message creation
        # - Check if it's a command
        # - Check if it's a question
        # - Process natural language
        return {"success": True, "action": "message_processed"}

    async def _handle_message_updated(self, event: BaseEvent) -> Dict[str, Any]:
        # Implementation for message updates
        return {"success": True, "action": "message_updated"}
