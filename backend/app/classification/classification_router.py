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

                return {
                    "needs_devrel": result.get("needs_devrel", False),
                    "priority": result.get("priority", "low"),
                    "reasoning": result.get("reasoning", "LLM classification"),
                    "original_message": message
                }

            return self._fallback_triage(message)

        except Exception as e:
            logger.error(f"Triage error: {str(e)}")
            return self._fallback_triage(message)

    def _fallback_triage(self, message: str) -> Dict[str, Any]:
        """Fallback: be conservative and assume it doesn't need DevRel help"""
        return {
            "needs_devrel": False,
            "priority": "low",
            "reasoning": "Fallback - conservative approach, no DevRel assistance needed",
            "original_message": message
        }
