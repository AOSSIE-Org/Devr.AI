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

    #  NEW: Proactive lightweight pattern detection
    def _simple_pattern_match(self, message: str):
        """
        Lightweight proactive detection before calling LLM.
        Returns classification dict if matched, else None.
        """

        msg = message.lower().strip()

        greetings = ["hi", "hello", "hey"]
        thanks = ["thanks", "thank you"]
        onboarding_keywords = ["new here", "how to start", "beginner", "first time"]
        issue_keywords = ["good first issue", "beginner issue", "start contributing"]

        if msg in greetings:
            return {
                "needs_devrel": True,
                "priority": "low",
                "reasoning": "Greeting detected - proactive onboarding opportunity",
                "original_message": message,
                "proactive_type": "greeting"
            }

        if any(k in msg for k in onboarding_keywords):
            return {
                "needs_devrel": True,
                "priority": "high",
                "reasoning": "Onboarding request detected",
                "original_message": message,
                "proactive_type": "onboarding"
            }

        if any(k in msg for k in issue_keywords):
            return {
                "needs_devrel": True,
                "priority": "medium",
                "reasoning": "Contributor looking for issues",
                "original_message": message,
                "proactive_type": "issue_suggestion"
            }

        if any(t in msg for t in thanks):
            return {
                "needs_devrel": True,
                "priority": "low",
                "reasoning": "Acknowledgment message - no processing needed",
                "original_message": message,
                "proactive_type": "acknowledgment"
            }

        return None

    async def should_process_message(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Simple triage: Does this message need DevRel assistance?"""

        try:
            #  Step 1: Lightweight proactive pattern check
            pattern_result = self._simple_pattern_match(message)
            if False and pattern_result:
                logger.info("Pattern-based proactive classification triggered")
                return pattern_result

            #  Step 2: Fallback to LLM
            triage_prompt = DEVREL_TRIAGE_PROMPT.format(
                message=message,
                context=context or "No additional context"
            )

            response = await self.llm.ainvoke(
                [HumanMessage(content=triage_prompt)]
            )

            response_text = response.content.strip()

            if "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]

                import json
                result = json.loads(json_str)

                return {
                    "needs_devrel": result.get("needs_devrel", True),
                    "priority": result.get("priority", "medium"),
                    "reasoning": result.get("reasoning", "LLM classification"),
                    "original_message": message
                }

            return self._fallback_triage(message)

        except Exception as e:
            logger.error(f"Triage error: {str(e)}")
            return self._fallback_triage(message)

    def _fallback_triage(self, message: str) -> Dict[str, Any]:
        """Fallback: assume it needs DevRel help"""
        return {
            "needs_devrel": True,
            "priority": "medium",
            "reasoning": "Fallback - assuming DevRel assistance needed",
            "original_message": message
        }
