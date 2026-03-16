import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class SecureHeadersMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, hsts_seconds: int = 63072000):
        super().__init__(app)
        self.hsts_seconds = hsts_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:

        response = await call_next(request)

        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = f"max-age={self.hsts_seconds}; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:

        ip = request.client.host if request.client else "unknown"
        now = time.time()

        queue = self._requests[ip]

        while queue and queue[0] + self.window_seconds < now:
            queue.pop(0)

        if len(queue) >= self.max_requests:
            return Response(
                status_code=429,
                content="Rate limit exceeded. Try again later."
            )

        queue.append(now)

        return await call_next(request)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: Callable) -> Response:

        try:
            return await call_next(request)

        except Exception:
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )


class AuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

        # Public routes (no login required)
        self.public_paths = [
            "/login",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/login/json",
            "/api/v1/auth/register"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:

        path = request.url.path

        # Allow OPTIONS requests (important for browser requests)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Allow static assets
        if path.startswith("/static"):
            return await call_next(request)

        # Allow public routes
        for public in self.public_paths:
            if path.startswith(public):
                return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):

            # If HTML request → redirect to login page
            if "text/html" in request.headers.get("accept", ""):
                return RedirectResponse(url="/login", status_code=302)

            return Response(status_code=401, content="Unauthorized")

        return await call_next(request)