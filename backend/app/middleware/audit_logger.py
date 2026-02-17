"""Audit Logger Middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import get_logger

logger = get_logger("audit")


class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """Logs all API access for audit trail"""

    SKIP_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            "api_request",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", ""),
        )

        response = await call_next(request)

        # Log response
        logger.info(
            "api_response",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )

        return response
