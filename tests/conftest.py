"""Shared pytest fixtures for support_chatbot tests."""

import pytest
from fastapi.testclient import TestClient

from support_chatbot.api.app import create_app
from support_chatbot.domain.models import (
    AskRequest,
    AskResponse,
    FeedbackRequest,
    IngestManualRequest,
    IngestManualResponse,
    Source,
)
from support_chatbot.settings import AppSettings


class FakeChatService:
    """Minimal chat service double used by route tests."""

    def __init__(self) -> None:
        """Track the last feedback submitted for assertions."""
        self.last_feedback: FeedbackRequest | None = None

    def ask(self, request: AskRequest) -> AskResponse:
        """Echo the request arguments in a predictable response."""
        return AskResponse(
            answer=f"echo:{request.question}:{request.session_id}:{request.manual_id}",
            trace_id="trace-123",
            sources=(
                Source(
                    url="https://example.org/manual/page",
                    title="Example Page",
                    score=0.87,
                ),
            ),
        )

    def submit_feedback(self, request: FeedbackRequest) -> None:
        """Record the feedback request for later assertions."""
        self.last_feedback = request


class FakeIngestionService:
    """Minimal manual ingestion service double used by route tests."""

    def ingest(self, request: IngestManualRequest) -> IngestManualResponse:
        """Return a predictable indexing summary for assertions."""
        return IngestManualResponse(
            documents_indexed=3,
            index_name=f"support-chatbot-index-{request.manual_id}",
        )


def build_test_settings() -> AppSettings:
    """Build the static settings object used by the test app."""
    return AppSettings.model_validate(
        {
            "PORT": 8000,
            "AUTH_API_KEY": "read-key",
            "AUTH_API_KEY_WRITE": "write-key",
            "VECTOR_STORE_ADDRESS": "https://example.search.windows.net",
            "VECTOR_STORE_PASSWORD": "dummy",
            "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com",
            "AZURE_OPENAI_API_KEY": "dummy",
            "AZURE_OPENAI_API_VERSION": "2024-06-01",
            "MODEL_CHAT": "gpt-4o-mini",
            "MODEL_EMBEDDINGS": "text-embedding-3-small",
        }
    )


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient wired with fake services."""
    app = create_app(
        settings=build_test_settings(),
        chat_service_factory=lambda _: FakeChatService(),
        ingestion_service_factory=lambda _: FakeIngestionService(),
    )
    with TestClient(app) as test_client:
        yield test_client
