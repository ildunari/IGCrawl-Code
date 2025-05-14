import time
import random
import json
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque
import redis
from ..config import get_settings

settings = get_settings()


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for Instagram API calls.
    Based on community-discovered limits:
    - Hard cap: 200 requests/hour per IP/session
    - Safe rate: 2 requests/minute (120/hour)
    - Sliding window: 11 minutes (~20 requests)
    """
    
    def __init__(self, redis_conn: Optional[redis.Redis] = None):
        self.redis_conn = redis_conn or redis.from_url(settings.redis_url)
        self.window_minutes = 11  # Instagram's sliding window
        self.requests_per_minute = settings.rate_limit_per_minute
        self.max_requests_per_window = 20  # ~20 requests per 11 minutes
        self.max_requests_per_hour = 180  # Stay under 200 hard cap
        
        # Jitter settings
        self.jitter_min = getattr(settings, 'jitter_seconds_min', 5)
        self.jitter_max = getattr(settings, 'jitter_seconds_max', 15)
        
    def _get_key(self, identifier: str) -> str:
        """Get Redis key for rate limit tracking"""
        return f"rate_limit:{identifier}"
    
    def _get_backoff_key(self, identifier: str) -> str:
        """Get Redis key for backoff tracking"""
        return f"backoff:{identifier}"
    
    def can_make_request(self, identifier: str) -> tuple[bool, Optional[float]]:
        """
        Check if request can be made and return wait time if not.
        Returns: (can_request, wait_seconds)
        """
        # Check if in backoff period
        backoff_until = self.redis_conn.get(self._get_backoff_key(identifier))
        if backoff_until:
            backoff_time = float(backoff_until)
            if time.time() < backoff_time:
                return False, backoff_time - time.time()
        
        # Get request history
        key = self._get_key(identifier)
        now = time.time()
        window_start = now - (self.window_minutes * 60)
        hour_start = now - 3600
        
        # Clean old entries
        self.redis_conn.zremrangebyscore(key, 0, window_start)
        
        # Count requests in sliding window
        window_count = self.redis_conn.zcount(key, window_start, now)
        hour_count = self.redis_conn.zcount(key, hour_start, now)
        
        # Check limits
        if window_count >= self.max_requests_per_window:
            # Find oldest request in window to calculate wait time
            oldest = self.redis_conn.zrange(key, 0, 0, withscores=True)
            if oldest:
                wait_time = (oldest[0][1] + (self.window_minutes * 60)) - now
                return False, max(wait_time, 1)
            return False, 60  # Default wait
        
        if hour_count >= self.max_requests_per_hour:
            # Find oldest request in hour to calculate wait time
            oldest = self.redis_conn.zrange(key, 0, 0, withscores=True)
            if oldest:
                wait_time = (oldest[0][1] + 3600) - now
                return False, max(wait_time, 1)
            return False, 60  # Default wait
        
        # Check per-minute rate
        minute_start = now - 60
        minute_count = self.redis_conn.zcount(key, minute_start, now)
        
        if minute_count >= self.requests_per_minute:
            # Wait until next minute
            wait_time = 60 - (now - minute_start)
            return False, max(wait_time, 1)
        
        return True, None
    
    def record_request(self, identifier: str):
        """Record a request was made"""
        key = self._get_key(identifier)
        now = time.time()
        self.redis_conn.zadd(key, {str(now): now})
        self.redis_conn.expire(key, 3600)  # Expire after 1 hour
    
    def record_rate_limit_hit(self, identifier: str):
        """Record that we hit a rate limit (429 response)"""
        # Implement exponential backoff
        backoff_key = self._get_backoff_key(identifier)
        current_backoff = self.redis_conn.get(backoff_key)
        
        if current_backoff:
            # Double the backoff period
            backoff_seconds = min(float(current_backoff) * 2, 3600)  # Max 1 hour
        else:
            # Initial backoff: 5 minutes
            backoff_seconds = 300
        
        backoff_until = time.time() + backoff_seconds
        self.redis_conn.setex(backoff_key, int(backoff_seconds), str(backoff_until))
        
        return backoff_seconds
    
    def get_delay_with_jitter(self) -> float:
        """Get delay between requests with random jitter"""
        base_delay = settings.scrape_delay_seconds
        jitter = random.uniform(self.jitter_min, self.jitter_max)
        return base_delay + jitter


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, rate_limiter: SlidingWindowRateLimiter):
        self.app = app
        self.rate_limiter = rate_limiter
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Skip rate limiting for OPTIONS requests (CORS preflight)
            if scope["method"] == "OPTIONS":
                await self.app(scope, receive, send)
                return
                
            # Extract identifier (IP address or user ID)
            client_ip = scope["client"][0] if scope["client"] else "unknown"
            identifier = f"ip:{client_ip}"
            
            # Check if this is an API endpoint that should be rate limited
            path = scope["path"]
            if path.startswith("/api/v1/scrapes") or path.startswith("/api/v1/export"):
                can_request, wait_time = self.rate_limiter.can_make_request(identifier)
                
                if not can_request:
                    # Get the origin header from the request
                    headers = dict(scope["headers"])
                    origin = headers.get(b"origin", b"").decode()
                    
                    # Determine allowed origin
                    allowed_origins = settings.cors_origins
                    if origin in allowed_origins:
                        cors_origin = origin
                    else:
                        cors_origin = allowed_origins[0] if allowed_origins else "*"
                    
                    response_body = {
                        "error": "Rate limit exceeded",
                        "retry_after": int(wait_time),
                        "message": f"Please wait {int(wait_time)} seconds before making another request"
                    }
                    
                    response_headers = [
                        (b"content-type", b"application/json"),
                        (b"retry-after", str(int(wait_time)).encode()),
                        (b"access-control-allow-origin", cors_origin.encode()),
                        (b"access-control-allow-methods", b"GET, POST, PUT, DELETE, OPTIONS"),
                        (b"access-control-allow-headers", b"*"),
                        (b"access-control-allow-credentials", b"true"),
                    ]
                    
                    await send({
                        "type": "http.response.start",
                        "status": 429,
                        "headers": response_headers,
                    })
                    await send({
                        "type": "http.response.body",
                        "body": json.dumps(response_body).encode(),
                    })
                    return
                
                # Record the request
                self.rate_limiter.record_request(identifier)
        
        await self.app(scope, receive, send)