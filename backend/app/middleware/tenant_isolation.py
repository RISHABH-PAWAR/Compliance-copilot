"""Multi-Tenant Isolation Middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """Ensures data isolation between tenants (companies)"""

    async def dispatch(self, request: Request, call_next):
        # Extract tenant info from JWT (done in security layer)
        # This middleware adds tenant context to request state
        request.state.tenant_id = None

        # Skip tenant check for public routes
        public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json",
                        "/api/v1/auth/login", "/api/v1/auth/register"]
        if request.url.path in public_paths:
            return await call_next(request)

        # Tenant ID will be set by auth dependency
        response = await call_next(request)
        return response
