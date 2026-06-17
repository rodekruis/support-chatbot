"""Request middleware for IDs and access logging."""

from __future__ import annotations

import logging
import secrets
import time

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class RequestIdMiddleware:
    """Attach a request id to each HTTP request and response."""

    def __init__(self, app: ASGIApp):
        """Store the downstream ASGI app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Attach a request id to HTTP requests and responses."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = f"req_{secrets.token_urlsafe(16)}"
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        async def send_with_request_id(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_request_id)


class RequestLoggingMiddleware:
    """Log request timing and status for each HTTP request."""

    def __init__(self, app: ASGIApp):
        """Store the downstream ASGI app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Log request timing and status after each HTTP call."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        await self.app(scope, receive, send_wrapper)

        elapsed_ms = round((time.perf_counter() - start) * 1000)
        logger.info(
            "request",
            extra={
                "method": scope.get("method"),
                "path": scope.get("path"),
                "status": status_code,
                "duration_ms": elapsed_ms,
                "request_id": scope.get("state", {}).get("request_id"),
            },
        )
