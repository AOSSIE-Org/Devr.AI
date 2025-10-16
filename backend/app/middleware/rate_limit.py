"""
Rate limiting middleware for API protection.
Prevents spam, abuse, and DoS attacks.
"""
import time
import logging
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
            burst_size: Max burst requests allowed
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Store: {ip: [(timestamp, count), ...]}
        self.request_history: Dict[str, list] = defaultdict(list)
        
        # Cleanup interval
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
    def _cleanup_old_requests(self):
        """Remove old request records to prevent memory bloat"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
            
        cutoff_time = current_time - 3600  # 1 hour ago
        
        for ip in list(self.request_history.keys()):
            self.request_history[ip] = [
                (ts, count) for ts, count in self.request_history[ip]
                if ts > cutoff_time
            ]
            
            if not self.request_history[ip]:
                del self.request_history[ip]
                
        self.last_cleanup = current_time
        logger.debug(f"Rate limiter cleanup complete. Active IPs: {len(self.request_history)}")
        
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed.
        
        Args:
            identifier: IP address or user ID
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        
        # Periodic cleanup
        self._cleanup_old_requests()
        
        history = self.request_history[identifier]
        
        # Check burst rate (last 60 seconds)
        recent_requests = [
            count for ts, count in history
            if ts > current_time - 60
        ]
        
        if sum(recent_requests) >= self.requests_per_minute:
            retry_after = 60
            logger.warning(f"Rate limit exceeded for {identifier} (per minute)")
            return False, retry_after
            
        # Check hourly rate
        hourly_requests = [
            count for ts, count in history
            if ts > current_time - 3600
        ]
        
        if sum(hourly_requests) >= self.requests_per_hour:
            retry_after = 3600
            logger.warning(f"Rate limit exceeded for {identifier} (per hour)")
            return False, retry_after
            
        # Check burst protection (multiple requests in same second)
        burst_requests = [
            count for ts, count in history
            if ts > current_time - 1
        ]
        
        if sum(burst_requests) >= self.burst_size:
            retry_after = 1
            logger.warning(f"Burst rate limit exceeded for {identifier}")
            return False, retry_after
            
        # Record this request
        history.append((current_time, 1))
        
        return True, None
        
    def get_rate_limit_headers(self, identifier: str) -> Dict[str, str]:
        """
        Get rate limit information headers.
        
        Args:
            identifier: IP address or user ID
            
        Returns:
            Dictionary of rate limit headers
        """
        current_time = time.time()
        history = self.request_history[identifier]
        
        # Count requests in last minute
        recent_count = sum(
            count for ts, count in history
            if ts > current_time - 60
        )
        
        # Count requests in last hour
        hourly_count = sum(
            count for ts, count in history
            if ts > current_time - 3600
        )
        
        return {
            "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
            "X-RateLimit-Remaining-Minute": str(max(0, self.requests_per_minute - recent_count)),
            "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
            "X-RateLimit-Remaining-Hour": str(max(0, self.requests_per_hour - hourly_count)),
        }


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
        exempt_paths: Optional[list] = None
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
            burst_size: Max burst size
            exempt_paths: List of paths to exempt from rate limiting
        """
        self.limiter = RateLimiter(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            burst_size=burst_size
        )
        self.exempt_paths = exempt_paths or ["/v1/health", "/favicon.ico"]
        
    def get_identifier(self, request: Request) -> str:
        """
        Get client identifier (IP or user ID).
        
        Args:
            request: FastAPI request
            
        Returns:
            Client identifier string
        """
        # Try to get real IP from headers (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
            
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        # Fall back to direct client IP
        if request.client:
            return request.client.host
            
        return "unknown"
        
    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
            
        identifier = self.get_identifier(request)
        
        # Check rate limit
        is_allowed, retry_after = self.limiter.is_allowed(identifier)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {identifier} on {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "message": f"Too many requests. Please try again in {retry_after} seconds."
                },
                headers={
                    "Retry-After": str(retry_after),
                    **self.limiter.get_rate_limit_headers(identifier)
                }
            )
            
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for key, value in self.limiter.get_rate_limit_headers(identifier).items():
            response.headers[key] = value
            
        return response


# Discord bot rate limiter
class DiscordRateLimiter:
    """
    Rate limiter specifically for Discord bot interactions.
    Prevents spam and abuse in Discord channels.
    """
    
    def __init__(
        self,
        messages_per_user_per_minute: int = 10,
        messages_per_channel_per_minute: int = 30
    ):
        """
        Initialize Discord rate limiter.
        
        Args:
            messages_per_user_per_minute: Max messages per user per minute
            messages_per_channel_per_minute: Max messages per channel per minute
        """
        self.messages_per_user_per_minute = messages_per_user_per_minute
        self.messages_per_channel_per_minute = messages_per_channel_per_minute
        
        self.user_history: Dict[str, list] = defaultdict(list)
        self.channel_history: Dict[str, list] = defaultdict(list)
        
    def is_user_allowed(self, user_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if user is allowed to send message.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Tuple of (is_allowed, cooldown_seconds)
        """
        current_time = time.time()
        cutoff = current_time - 60
        
        # Clean old records
        self.user_history[user_id] = [
            ts for ts in self.user_history[user_id]
            if ts > cutoff
        ]
        
        if len(self.user_history[user_id]) >= self.messages_per_user_per_minute:
            oldest = min(self.user_history[user_id])
            cooldown = int(60 - (current_time - oldest))
            return False, cooldown
            
        self.user_history[user_id].append(current_time)
        return True, None
        
    def is_channel_allowed(self, channel_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if channel can receive more messages.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            Tuple of (is_allowed, cooldown_seconds)
        """
        current_time = time.time()
        cutoff = current_time - 60
        
        # Clean old records
        self.channel_history[channel_id] = [
            ts for ts in self.channel_history[channel_id]
            if ts > cutoff
        ]
        
        if len(self.channel_history[channel_id]) >= self.messages_per_channel_per_minute:
            oldest = min(self.channel_history[channel_id])
            cooldown = int(60 - (current_time - oldest))
            return False, cooldown
            
        self.channel_history[channel_id].append(current_time)
        return True, None
