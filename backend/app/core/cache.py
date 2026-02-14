"""
In-memory cache utility with TTL support for GitHub API responses.
Production-ready caching layer with thread safety.
"""
import hashlib
import json
import logging
import time
from typing import Any, Optional, Callable
from threading import Lock

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a single cache entry with TTL."""

    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return (time.time() - self.created_at) > self.ttl_seconds

    def __repr__(self):
        remaining = self.ttl_seconds - (time.time() - self.created_at)
        return f"CacheEntry(TTL: {remaining:.1f}s remaining)"


class SimpleCache:
    """
    Thread-safe in-memory cache for API responses.
    Automatically invalidates expired entries.
    """

    def __init__(self, max_size: int = 1000):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate a cache key from prefix and kwargs."""
        key_str = f"{prefix}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if it exists and hasn't expired."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    self.hits += 1
                    logger.debug(f"Cache hit: {key} ({entry})")
                    return entry.value
                else:
                    # Remove expired entry
                    del self._cache[key]
                    self.misses += 1
                    logger.debug(f"Cache miss (expired): {key}")
                    return None
            self.misses += 1
            logger.debug(f"Cache miss: {key}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set value in cache with TTL."""
        with self._lock:
            # Ensure at least 1 entry is removed when cache exceeds max_size
            if len(self._cache) >= self.max_size:
                evict_count = max(1, int(self.max_size * 0.1))
                old_keys = sorted(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].created_at
                )[:evict_count]
                for old_key in old_keys:
                    del self._cache[old_key]
                logger.debug(f"Cache evicted {len(old_keys)} old entries")

            self._cache[key] = CacheEntry(value, ttl_seconds)
            logger.debug(f"Cache set: {key} (TTL: {ttl_seconds}s)")

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            size = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache cleared ({size} entries removed)")

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            return {
                "size": len(self._cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": f"{hit_rate:.1f}%",
                "total_requests": total_requests
            }

    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                logger.debug(f"Cache cleanup removed {len(expired_keys)} expired entries")
            return len(expired_keys)


# Global cache instance
_cache = SimpleCache(max_size=1000)


def get_cache() -> SimpleCache:
    """Get the global cache instance."""
    return _cache


def cache_result(prefix: str, ttl_seconds: int = 300):
    """
    Decorator to cache async function results.
    
    Args:
        prefix: Cache key prefix
        ttl_seconds: Time to live for cached result (default: 5 minutes)
    
    Example:
        @cache_result("repo_stats", ttl_seconds=600)
        async def get_repo_stats(owner: str, repo: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            cache = get_cache()
            cache_key = cache._generate_key(prefix, args=args, kwargs=kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            if result is not None:
                cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator
