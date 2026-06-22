"""Exception handlers and API error responses."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from support_chatbot.api.schemas import ErrorResponse
from support_chatbot.domain.errors import ExternalServiceError

logger = logging.getLogger(__name__)


def _error_response(
    status_code: int, code: str, message: str, request: Request
) -> JSONResponse:
    request_id = None
    if hasattr(request, "state"):
        request_id = getattr(request.state, "request_id", None)

    payload = ErrorResponse(
        error={"code": code, "message": message, "request_id": request_id}
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Register API-wide exception handlers on the application."""

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return _error_response(422, "validation_error", str(exc), request)

    @app.exception_handler(ExternalServiceError)
    async def external_service_error_handler(
        request: Request, exc: ExternalServiceError
    ):
        logger.error("External service error: %s", exc)
        return _error_response(502, "external_service_error", str(exc), request)

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error")
        return _error_response(
            500, "internal_error", "An unexpected error occurred", request
        )
