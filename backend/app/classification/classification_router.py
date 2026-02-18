import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from .prompt import DEVREL_TRIAGE_PROMPT

logger = logging.getLogger(__name__)

class ClassificationRouter:
    """Simple DevRel triage - determines if message needs DevRel assistance"""

    def __init__(self, llm_client=None):
        self.llm = llm_client or ChatGoogleGenerativeAI(
            model=settings.classification_agent_model,
            temperature=0.1,
            google_api_key=settings.gemini_api_key
        )

    async def should_process_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simple triage: Does this message need DevRel assistance?"""
        try:
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

                # FIXED: Default to False instead of True
                return {
                    "needs_devrel": result.get("needs_devrel", False),  # ← CHANGED!
                    "priority": result.get("priority", "low"),
                    "reasoning": result.get("reasoning", "LLM classification"),
                    "original_message": message
                }

            # FIXED: If no JSON found, don't respond
            logger.warning(f"No JSON in classification response for: {message[:50]}")
            return self._fallback_triage(message)

        except Exception as e:
            logger.error(f"Triage error: {str(e)}")
            return self._fallback_triage(message)

    def _fallback_triage(self, message: str) -> Dict[str, Any]:
        """Fallback: IGNORE message when classification fails"""
        # FIXED: Changed to False - better to miss a message than spam
        logger.warning(f"Classification failed, IGNORING message: {message[:50]}")
        return {
            "needs_devrel": False,  # ← CHANGED FROM TRUE TO FALSE!
            "priority": "low",
            "reasoning": "Fallback - classification failed, ignoring for safety",
            "original_message": message
        }