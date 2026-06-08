"""Shared pytest fixtures for support_chatbot tests."""

import pytest
from fastapi.testclient import TestClient

from support_chatbot.api.app import create_app
from support_chatbot.services.vector_store_service import ManualUpdateResult
from support_chatbot.settings import AppSettings


class FakeChatService:
    """Minimal chat service double used by route tests."""

    def ask(self, question: str, thread_id: str, manual_id: str | None = None) -> str:
        """Echo the request arguments in a predictable response."""
        return f"echo:{question}:{thread_id}:{manual_id}"


class FakeVectorStoreService:
    """Minimal vector store service double used by route tests."""

    def update_from_manual(self, manual_id: str | None = None) -> ManualUpdateResult:
        """Return a predictable indexing summary for assertions."""
        return ManualUpdateResult(
            documents_indexed=3,
            index_name=f"support-chatbot-index-{manual_id or '121'}",
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
            "VECTOR_STORE_ID": "support-chatbot-index",
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
        vector_store_service_factory=lambda _: FakeVectorStoreService(),
    )
    with TestClient(app) as test_client:
        yield test_client
