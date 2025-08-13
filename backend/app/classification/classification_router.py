import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from .prompt import DEVREL_TRIAGE_PROMPT

logger = logging.getLogger(__name__)

class ClassificationRouter:
    """Strict DevRel triage - determines if message needs DevRel assistance"""

    def __init__(self, llm_client=None):
        self.bot_name = settings.bot_name.lower()
        self.llm = llm_client or ChatGoogleGenerativeAI(
            model=settings.classification_agent_model,
            temperature=0.1,
            google_api_key=settings.gemini_api_key
        )

    async def should_process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Strict triage: Does this message need DevRel assistance?"""
        try:
            # Detect explicit bot mention
            mention_flag = False
            if self.bot_name in message.lower():
                mention_flag = True
                # Add note to the context so LLM knows it was mentioned
                context = (context or '') + f" | Note: This message explicitly mentions the bot '{self.bot_name}'."

            triage_prompt = DEVREL_TRIAGE_PROMPT.format(
                message=message,
                context=context or 'No additional context'
            )

            response = await self.llm.ainvoke([HumanMessage(content=triage_prompt)])
            response_text = response.content.strip()

            if '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]

                import json
                result = json.loads(json_str)

                return {
                    "needs_devrel": result.get("needs_devrel", False),
                    "priority": result.get("priority", "medium"),
                    "reasoning": result.get("reasoning", "LLM classification"),
                    "original_message": message,
                    "bot_mentioned": mention_flag
                }

            return self._fallback_triage(message, mention_flag)

        except Exception as e:
            logger.error(f"Triage error: {str(e)}")
            return self._fallback_triage(message)

    def _fallback_triage(self, message: str, mention_flag=False) -> Dict[str, Any]:
        """Fallback: only trigger DevRel if bot was mentioned and message looks relevant"""
        return {
            "needs_devrel": mention_flag,
            "priority": "medium" if mention_flag else "low",
            "reasoning": "Fallback - bot mention" if mention_flag else "Fallback - no DevRel assistance",
            "original_message": message,
            "bot_mentioned": mention_flag
        }
