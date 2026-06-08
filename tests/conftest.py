import pytest
from fastapi.testclient import TestClient

from support_chatbot.api.app import create_app
from support_chatbot.settings import AppSettings


class FakeChatService:
    def ask(self, question: str, thread_id: str) -> str:
        return f"echo:{question}:{thread_id}"


class FakeVectorStoreService:
    def update_from_manual(self) -> int:
        return 3


def build_test_settings() -> AppSettings:
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
    app = create_app(
        settings=build_test_settings(),
        chat_service_factory=lambda _: FakeChatService(),
        vector_store_service_factory=lambda _: FakeVectorStoreService(),
    )
    with TestClient(app) as test_client:
        yield test_client
