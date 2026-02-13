import re
import time
import asyncio
import logging
from typing import Optional, Dict, Any
from cachetools import TTLCache
from collections import Counter
from langchain_core.messages import HumanMessage
import hashlib
import json

logger = logging.getLogger(__name__)

try:
    import xxhash
    _HAS_XXHASH = True
except Exception:
    xxhash = None
    _HAS_XXHASH = False

# Config
CACHE_MAXSIZE = 4096
CACHE_TTL_SECONDS = 60 * 60
MAX_MESSAGE_LENGTH = 10000  # Max message length to process (prevents DoS via large payloads)

# Patterns for fast-path classification (concise to reduce memory)
# Merge related intents into fewer regexes and add common Discord patterns
_PATTERNS = {
    # common salutations
    "greeting": re.compile(r"^\s*(?:hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening)\b", re.I),
    # explicit help / action requests
    "action_request": re.compile(r".*\b(?:help|please\s+help|plz\s+help|need\s+help|support|assist|request)\b", re.I),
    # bug / error reports
    "bug_report": re.compile(r".*\b(?:bug|error|exception|stack\s*trace|crash|failed|traceback|segfault)\b", re.I),
    # thanks and short acknowledgements (shared fast-path)
    "thanks_ack": re.compile(r"^\s*(?:thanks|thank\s+you|thx|ty|ok|okay|got\s+it|roger|ack)\b", re.I),
    # modern short responses / slang that are non-actionable
    "slang": re.compile(r"^\s*(?:brb|lol|lmao|rofl|omg|wtf|smh|idk|np|yw|pls|plz|bump|ping|fyi|imo|idc)\b", re.I),
    # general intent bucket for optimization/performance/docs/feature keywords
    "intent_general": re.compile(
        r".*\b(?:optimi[sz]e|improve|speed\s*up|performance|memory|resource|efficient|documentation|docs|guide|tutorial|example|feature|suggest|idea)\b",
        re.I,
    ),
    # Discord-specific: user mentions (@user)
    "discord_mention": re.compile(r"(?:<@!?\d+>|@\w+)\b"),
    # Channel mentions (#channel or <#123456>)
    "channel_mention": re.compile(r"(?:<#\d+>|#\w+)\b"),
    # Bot/CLI-like commands commonly used on Discord (prefix-based)
    "command": re.compile(r"^\s*(?:/|!|\?|\.|\$)[A-Za-z0-9_\-]+"),
    # Code snippets or blocks (inline or triple backticks)
    "code_block": re.compile(r"```[\s\S]*?```|`[^`]+`", re.S),
    # URLs (simple detection)
    "url": re.compile(r"https?://\S+|www\.\S+"),
    # GitHub/issue/PR references (#123, owner/repo#123, PR #123)
    "pr_issue_ref": re.compile(r"(?:\b#\d+\b|\b[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#\d+\b|\bPR\s*#\d+\b)", re.I),
    # Emoji shortname like :emoji:
    "emoji_short": re.compile(r":[a-zA-Z0-9_+\-]+:"),
}

# Simple deterministic classifications for the patterns
# Keep mapping concise and reflect combined pattern keys
_PATTERN_CLASSIFICATION = {
    "greeting": {"needs_devrel": False, "priority": "low", "reasoning": "greeting"},
    "thanks_ack": {"needs_devrel": False, "priority": "low", "reasoning": "thanks/acknowledgement"},
    "slang": {"needs_devrel": False, "priority": "low", "reasoning": "short/slang response"},
    "action_request": {"needs_devrel": True, "priority": "high", "reasoning": "explicit help/request keywords"},
    "bug_report": {"needs_devrel": True, "priority": "high", "reasoning": "error or bug report"},
    "integration": {"needs_devrel": True, "priority": "high", "reasoning": "Discord/GitHub/integration requests (OAuth, commands, threads, repo ops)"},
    "architecture": {"needs_devrel": True, "priority": "medium", "reasoning": "architecture/infra mentions (queues, DBs, LLMs)"},
    "intent_general": {"needs_devrel": True, "priority": "medium", "reasoning": "optimization/docs/feature requests"},
    
    # Discord/GitHub specific quick classifications
    "discord_mention": {"needs_devrel": False, "priority": "low", "reasoning": "user mention"},
    "channel_mention": {"needs_devrel": False, "priority": "low", "reasoning": "channel mention"},
    "command": {"needs_devrel": False, "priority": "medium", "reasoning": "bot/CLI command invocation"},
    "code_block": {"needs_devrel": False, "priority": "low", "reasoning": "code snippet or block"},
    "url": {"needs_devrel": False, "priority": "low", "reasoning": "contains URL"},
    "pr_issue_ref": {"needs_devrel": True, "priority": "medium", "reasoning": "reference to issue or PR"},
    "emoji_short": {"needs_devrel": False, "priority": "low", "reasoning": "emoji shortname"},
}

_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL_SECONDS)
# In-flight calls to dedupe concurrent identical requests (bounded with TTL to prevent leaks)
_inflight: TTLCache = TTLCache(maxsize=1000, ttl=120)  # Max 1000 concurrent, 2min timeout

# Simple metrics
metrics = Counter({"total": 0, "cache_hits": 0, "cache_misses": 0, "skipped_llm": 0})


# Simple cache key generation
def make_key(model: str, prompt: str, params: Dict[str, Any]) -> str:
    """
    Create a stable cache key using XXHash128 for speed.
    - normalize prompt to reduce trivial differences
    - serialize params with sorted keys and compact separators
    - use blake2b as a fallback if xxhash unavailable
    """
    norm_prompt = normalize_message(prompt)

    # Serialize params once; for very large params consider hashing only relevant fields
    try:
        params_blob = json.dumps(params or {}, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    except Exception:
        params_blob = str(params).encode("utf-8")

    payload = b"|".join([model.encode("utf-8"), norm_prompt.encode("utf-8"), params_blob])

    # Use XXHash128 for better collision resistance (if available), otherwise fallback
    if _HAS_XXHASH:
        return xxhash.xxh3_128_hexdigest(payload)
    else:
        return hashlib.blake2b(payload, digest_size=16).hexdigest()


def _compose_prompt_with_context(normalized: str, context_id: Optional[str]) -> str:
    if context_id:
        return f"{normalized}|ctx:{context_id}"
    return normalized


def key_for_normalized(normalized: str, context_id: Optional[str], model: str, params: Dict[str, Any]) -> str:
    """
    Compute cache key from a normalized message and optional context id.
    """
    prompt = _compose_prompt_with_context(normalized, context_id)
    return make_key(model, prompt, params)


def get_cached_by_normalized(normalized: str, context_id: Optional[str], model: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Retrieve cached payload for a normalized message + context."""
    key = key_for_normalized(normalized, context_id, model, params)
    return cache_get(key)


def set_cached_by_normalized(normalized: str, context_id: Optional[str], model: str, params: Dict[str, Any], payload: Dict[str, Any]) -> None:
    """Store payload for normalized message + context."""
    key = key_for_normalized(normalized, context_id, model, params)
    cache_set(key, payload)


# Cache wrapper for LLM calls (async - uses llm.ainvoke)
async def cached_llm_call(prompt: str, model: str, params: Dict[str, Any], llm):
    """
    Cached wrapper for async LLM calls with:
    - fast-path simple pattern classification to avoid LLM cost
    - cache hit/miss metrics
    - in-flight deduplication so concurrent identical requests share one LLM call
    """
    # Fast-path: simple deterministic classification (avoid LLM)
    normalized = normalize_message(prompt)
    simple = is_simple_message(normalized)
    if simple is not None:
        metrics["skipped_llm"] += 1
        return simple

    metrics["total"] += 1
    key = make_key(model, prompt, params)

    # Quick cache check
    cached = cache_get(key)
    if cached is not None:
        metrics["cache_hits"] += 1
        return cached

    metrics["cache_misses"] += 1

    # Deduplicate in-flight identical calls so only one LLM request is made
    loop = asyncio.get_running_loop()
    # Attempt to install a future atomically to dedupe concurrent callers
    future = loop.create_future()
    prev = _inflight.setdefault(key, future)
    if prev is not future:
        # another caller is in-flight; await its result/failure
        return await prev

    # we are the owner; perform the fetch and set the future result/exception
    async def _owner_fetch():
        try:
            start = time.time()
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            elapsed = time.time() - start
            # log elapsed to avoid unused variable and help with metrics/troubleshooting
            logger.debug(f"LLM call elapsed for key {key}: {elapsed:.3f}s", extra={"elapsed": elapsed})
            # store response content or small payload rather than full object
            result = response.content if hasattr(response, "content") else response
            _cache[key] = result
            future.set_result(result)
            return result
        except asyncio.CancelledError:
            future.cancel()
            raise
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # ensure inflight entry removed
            _inflight.pop(key, None)

    # schedule owner fetch and await its result
    owner_task = loop.create_task(_owner_fetch())

    # callback to ensure exceptions from the background task are propagated to waiting callers
    def _owner_done(task: asyncio.Task) -> None:
        try:
            exc = task.exception()
        except asyncio.CancelledError:
            # task was cancelled, nothing to propagate here
            return
        if exc is not None and not future.done():
            future.set_exception(exc)

    owner_task.add_done_callback(_owner_done)

    try:
        return await future
    except asyncio.CancelledError:
        # If the awaiting coroutine is cancelled, cancel the owner task and wait for it to finish
        owner_task.cancel()
        try:
            await owner_task
        except asyncio.CancelledError:
            # owner_task was cancelled as well; swallow to avoid masking original cancellation
            pass
        raise
    
def normalize_message(msg: str) -> str:
    """Normalize message for caching. Truncates to MAX_MESSAGE_LENGTH to prevent DoS."""
    s = (msg or "")[:MAX_MESSAGE_LENGTH].strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def is_simple_message(normalized: str) -> Optional[Dict[str, Any]]:
    for name, pattern in _PATTERNS.items():
        if pattern.match(normalized):
            return dict(_PATTERN_CLASSIFICATION[name], original_message=normalized)
    return None

def cache_get(key: str) -> Optional[Dict[str, Any]]:
    try:
        return _cache[key]
    except KeyError:
        return None


def cache_set(key: str, value: Dict[str, Any]) -> None:
    """Store value in cache."""
    _cache[key] = value