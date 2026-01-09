"""
Rate Limiting Middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from ..core.rate_limiter import rate_limiter
import time

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/api/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # Get client identifier (IP address)
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    is_allowed, info = rate_limiter.is_allowed(
        endpoint=request.url.path,
        identifier=client_ip
    )
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Try again in {info.get('retry_after', 0)} seconds.",
                "limit": info.get("limit"),
                "window": info.get("window"),
                "retry_after": info.get("retry_after", 0)
            },
            headers={
                "X-RateLimit-Limit": str(info.get("limit", 0)),
                "X-RateLimit-Remaining": str(info.get("remaining", 0)),
                "X-RateLimit-Reset": str(int(info.get("reset_at", time.time()))),
                "Retry-After": str(info.get("retry_after", 0))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(info.get("limit", 0))
    response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
    response.headers["X-RateLimit-Reset"] = str(int(info.get("reset_at", time.time())))
    
    return response
