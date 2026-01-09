"""
Rate Limiter - Simple in-memory rate limiting
"""
from typing import Dict, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._limits: Dict[str, Tuple[int, int]] = {}  # endpoint -> (max_requests, window_seconds)
    
    def set_limit(self, endpoint: str, max_requests: int, window_seconds: int):
        """Set rate limit for an endpoint."""
        self._limits[endpoint] = (max_requests, window_seconds)
    
    def is_allowed(self, endpoint: str, identifier: str = "default") -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed.
        Returns (is_allowed, info_dict)
        """
        if endpoint not in self._limits:
            return True, {}
        
        max_requests, window_seconds = self._limits[endpoint]
        key = f"{endpoint}:{identifier}"
        
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self._requests[key]) >= max_requests:
            oldest_request = min(self._requests[key])
            reset_time = oldest_request + window_seconds
            retry_after = int(reset_time - now)
            
            return False, {
                "limit": max_requests,
                "window": window_seconds,
                "remaining": 0,
                "reset_at": reset_time,
                "retry_after": retry_after
            }
        
        # Add current request
        self._requests[key].append(now)
        
        remaining = max_requests - len(self._requests[key])
        oldest_request = min(self._requests[key]) if self._requests[key] else now
        reset_time = oldest_request + window_seconds
        
        return True, {
            "limit": max_requests,
            "window": window_seconds,
            "remaining": remaining,
            "reset_at": reset_time
        }
    
    def reset(self, endpoint: str = None, identifier: str = None):
        """Reset rate limit for endpoint/identifier."""
        if endpoint and identifier:
            key = f"{endpoint}:{identifier}"
            if key in self._requests:
                del self._requests[key]
        elif endpoint:
            # Reset all identifiers for endpoint
            keys_to_delete = [k for k in self._requests.keys() if k.startswith(f"{endpoint}:")]
            for key in keys_to_delete:
                del self._requests[key]
        else:
            # Reset all
            self._requests.clear()


# Global rate limiter instance
rate_limiter = RateLimiter()

# Set default limits
rate_limiter.set_limit("/api/generate", max_requests=10, window_seconds=60)  # 10 per minute
rate_limiter.set_limit("/api/files", max_requests=100, window_seconds=60)  # 100 per minute
rate_limiter.set_limit("/api/status", max_requests=200, window_seconds=60)  # 200 per minute
