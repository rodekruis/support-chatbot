"""FastAPI dependency helpers and API key guards."""

import secrets

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from support_chatbot.settings import AppSettings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_settings(request: Request) -> AppSettings:
    """Return the shared application settings object."""
    return request.app.state.settings


def get_chat_service(request: Request):
    """Return the initialized chat service."""
    return request.app.state.chat_service


def get_ingestion_service(request: Request):
    """Return the initialized manual ingestion service."""
    return request.app.state.ingestion_service


def _require_key(provided_key: str | None, expected_key: str, code: str) -> None:
    if not provided_key or not secrets.compare_digest(provided_key, expected_key):
        raise HTTPException(status_code=401, detail=code)


def require_read_key(
    api_key: str | None = Security(api_key_header),
    settings: AppSettings = Depends(get_settings),
) -> None:
    """Require the read API key for chat endpoints."""
    _require_key(
        provided_key=api_key,
        expected_key=settings.auth_api_key.get_secret_value(),
        code="invalid_or_missing_api_key",
    )


def require_write_key(
    api_key: str | None = Security(api_key_header),
    settings: AppSettings = Depends(get_settings),
) -> None:
    """Require the write API key for admin endpoints."""
    _require_key(
        provided_key=api_key,
        expected_key=settings.auth_api_key_write.get_secret_value(),
        code="invalid_or_missing_write_key",
    )
