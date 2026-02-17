"""Rate Limiter Middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware using Redis or in-memory fallback"""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = {}  # In-memory fallback

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        # Try Redis first, fall back to in-memory
        try:
            from app.core.cache import cache
            count = await cache.increment(key, self.window_seconds)
            if count and count > self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                )
        except Exception:
            # In-memory fallback
            import time
            now = time.time()
            if key in self._requests:
                requests, window_start = self._requests[key]
                if now - window_start > self.window_seconds:
                    self._requests[key] = (1, now)
                elif requests >= self.max_requests:
                    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
                else:
                    self._requests[key] = (requests + 1, window_start)
            else:
                self._requests[key] = (1, now)

        return await call_next(request)
