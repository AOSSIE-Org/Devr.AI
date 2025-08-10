import logging
from typing import Dict, Any
from app.core.events.base import BaseEvent
from app.core.events.enums import EventType
from app.core.handler.base import BaseHandler

logger = logging.getLogger(__name__)

class FAQHandler(BaseHandler):
    """Handler for FAQ and knowledge base queries"""

    def __init__(self, bot=None):
        self.bot = bot
        self.faq_responses = {
            "what is devr.ai?": "Devr.AI is an AI-powered Developer Relations assistant that helps open-source communities by automating engagement and issue tracking.",
            "how do i contribute?": "You can contribute by visiting our GitHub repo, checking open issues, and submitting pull requests.",
            "what platforms does devr.ai support?": "Devr.AI integrates with Discord, Slack, GitHub, and Discourse to assist developers and maintainers.",
            "who maintains devr.ai?": "Devr.AI is maintained by an open-source community of developers.",
            "how do i report a bug?": "You can report a bug by opening an issue on our GitHub repository.",
        }

    async def is_faq(self, message: str):
        """Check if the question is in the FAQ and return the response"""
        for key in self.faq_responses:
            if message.lower() == key.lower():
                return True, self.faq_responses[key]
        return False, None

    async def handle(self, event: BaseEvent) -> Dict[str, Any]:
        logger.info(f"Handling FAQ request event: {event.event_type}")

        if event.event_type == EventType.FAQ_REQUESTED:
            return await self._handle_faq_request(event)
        elif event.event_type == EventType.KNOWLEDGE_UPDATED:
            return await self._handle_knowledge_update(event)
        else:
            logger.warning(f"Unsupported FAQ event type: {event.event_type}")
            return {"success": False, "reason": "Unsupported event type"}

    async def _handle_faq_request(self, event: BaseEvent) -> Dict[str, Any]:
        question = (event.content or "").strip().lower()
        response = self.get_faq_response(question)

        logger.info("Question: " + question + ", Response: " + response)

        await self._send_discord_response(event.channel_id, response)
        return {"success": True, "action": "faq_response_sent"}

    def get_faq_response(self, question: str) -> str:
        return self.faq_responses.get(question.lower(), "I'm not sure about that, but I can find out!")

    async def _handle_knowledge_update(self, event: BaseEvent) -> Dict[str, Any]:
        """Handles knowledge base updates."""
        return {"success": True, "action": "knowledge_updated"}

    async def _send_discord_response(self, channel_id: str, response: str):
        """Sends a response message to the specified Discord channel."""
        if self.bot:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(response)
            else:
                logger.error(f"Could not find Discord channel with ID {channel_id}")
