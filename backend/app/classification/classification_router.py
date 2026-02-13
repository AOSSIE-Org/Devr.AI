import asyncio
import logging
import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from .prompt import DEVREL_TRIAGE_PROMPT
from app.classification.cache_helpers import (
    normalize_message,
    is_simple_message,
    get_cached_by_normalized,
    set_cached_by_normalized,
    metrics,
    MAX_MESSAGE_LENGTH,
)

logger = logging.getLogger(__name__)

# Limit concurrent LLM calls to prevent rate limiting and cost explosions
_LLM_SEMAPHORE = asyncio.Semaphore(10)


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
            # Early return for oversized messages to prevent DoS
            if len(message) > MAX_MESSAGE_LENGTH:
                logger.warning(f"Message exceeds max length ({len(message)} > {MAX_MESSAGE_LENGTH}), using fallback")
                return self._fallback_triage(message[:MAX_MESSAGE_LENGTH])

            metrics["total"] += 1
            normalized = normalize_message(message)

            # fast-path: simple pattern match (no LLM)
            simple = is_simple_message(normalized)

            if simple is not None:
                metrics["skipped_llm"] += 1
                return simple

            # cache lookup (include a light context fingerprint if present)
            ctx_id = None
            if context:
                ctx_id = context.get("channel_id") or context.get("thread_id") or ""
                if not ctx_id:
                    ctx_id = None

            cached = get_cached_by_normalized(normalized, ctx_id, settings.classification_agent_model, {"temperature": 0.1})
            if cached is not None:
                metrics["cache_hits"] += 1
                return cached

            metrics["cache_misses"] += 1

            triage_prompt = DEVREL_TRIAGE_PROMPT.format(
                message=message,
                context=context or 'No additional context'
            )

            # Use semaphore to limit concurrent LLM calls
            async with _LLM_SEMAPHORE:
                response = await self.llm.ainvoke([HumanMessage(content=triage_prompt)])
            response_text = response.content.strip()

            if '{' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)

                payload = {
                    "needs_devrel": result.get("needs_devrel", True),
                    "priority": result.get("priority", "medium"),
                    "reasoning": result.get("reasoning", "LLM classification"),
                    "original_message": message
                }
                set_cached_by_normalized(normalized, ctx_id, settings.classification_agent_model, {"temperature": 0.1}, payload)
                return payload

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
