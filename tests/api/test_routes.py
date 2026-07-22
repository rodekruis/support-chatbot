"""API route tests for support_chatbot."""

from fastapi.testclient import TestClient

from support_chatbot.api.app import create_app
from support_chatbot.domain.errors import ExternalServiceError
from tests.conftest import FakeChatService, build_test_settings


def test_ask_requires_read_key(client):
    """Reject chat requests without the read API key."""
    response = client.post("/ask", json={"question": "hello", "manual_id": "121"})
    assert response.status_code == 401


def test_ask_stream_requires_read_key(client):
    """Reject streaming chat requests without the read API key."""
    response = client.post(
        "/ask/stream", json={"question": "hello", "manual_id": "121"}
    )
    assert response.status_code == 401


def test_ask_stream_yields_token_and_done_events(client):
    """Stream NDJSON token events followed by a terminal done event."""
    import json

    response = client.post(
        "/ask/stream",
        headers={"Authorization": "read-key"},
        json={"question": "hello", "manual_id": "121"},
    )
    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.splitlines() if line]

    tokens = [e for e in events if e["type"] == "token"]
    done = [e for e in events if e["type"] == "done"]
    assert "".join(t["text"] for t in tokens) == "echo:hello:121"
    assert len(done) == 1
    assert done[0]["trace_id"] == "trace-123"
    assert done[0]["sources"][0]["url"] == "https://example.org/manual/page"


def test_ask_returns_answer_with_read_key(client):
    """Return the chat answer when the read API key is present."""
    response = client.post(
        "/ask",
        headers={"Authorization": "read-key"},
        json={"question": "hello", "manual_id": "121"},
    )
    assert response.status_code == 200
    assert response.json()["answer"].startswith("echo:hello")


def test_ask_passes_manual_id(client):
    """Forward the manual id from the request body to the chat service."""
    response = client.post(
        "/ask",
        headers={"Authorization": "read-key"},
        json={"question": "hello", "manual_id": "121"},
    )
    assert response.status_code == 200
    assert response.json()["answer"].endswith(":121")


def test_ask_returns_trace_id(client):
    """Expose the observability trace id so it can be scored via /feedback."""
    response = client.post(
        "/ask",
        headers={"Authorization": "read-key"},
        json={"question": "hello", "manual_id": "121"},
    )
    assert response.status_code == 200
    assert response.json()["trace_id"] == "trace-123"


def test_ask_returns_sources(client):
    """Expose the manual pages that backed the answer with their links."""
    response = client.post(
        "/ask",
        headers={"Authorization": "read-key"},
        json={"question": "hello", "manual_id": "121"},
    )
    assert response.status_code == 200
    sources = response.json()["sources"]
    assert sources == [
        {
            "url": "https://example.org/manual/page",
            "title": "Example Page",
            "score": 0.87,
        }
    ]


def test_feedback_requires_read_key(client):
    """Reject feedback submissions without the read API key."""
    response = client.post(
        "/feedback",
        json={"trace_id": "trace-123", "positive": True},
    )
    assert response.status_code == 401


def test_feedback_accepts_thumbs_up(client):
    """Record a thumbs-up score for a previously generated answer."""
    response = client.post(
        "/feedback",
        headers={"Authorization": "read-key"},
        json={"trace_id": "trace-123", "positive": True, "comment": "great"},
    )
    assert response.status_code == 202
    assert response.json()["message"] == "Feedback accepted."


def test_ingest_manual_requires_write_key(client):
    """Reject manual ingestion without the write API key."""
    response = client.post(
        "/ingest-manual",
        headers={"Authorization": "read-key"},
        params={"manual_id": "121"},
    )
    assert response.status_code == 401


def test_ingest_manual_with_write_key(client):
    """Return the indexing summary when the write API key is present."""
    response = client.post(
        "/ingest-manual",
        headers={"Authorization": "write-key"},
        params={"manual_id": "121"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["documents_indexed"] == 3
    assert payload["index_name"] == "support-chatbot-index-121"


def test_ingest_manual_with_manual_id(client):
    """Forward the manual id to the manual ingestion endpoint."""
    response = client.post(
        "/ingest-manual",
        headers={"Authorization": "write-key"},
        params={"manual_id": "demo"},
    )
    assert response.status_code == 200
    assert response.json()["index_name"] == "support-chatbot-index-demo"


def test_ingest_manual_external_service_error_returns_502():
    """Map an external service failure during ingestion to a 502 with details."""

    class FailingIngestionService:
        def ingest(self, request):
            raise ExternalServiceError(
                "Index quota has been exceeded for this service."
            )

    app = create_app(
        settings=build_test_settings(),
        chat_service_factory=lambda _: FakeChatService(),
        ingestion_service_factory=lambda _: FailingIngestionService(),
    )
    with TestClient(app) as test_client:
        response = test_client.post(
            "/ingest-manual",
            headers={"Authorization": "write-key"},
            params={"manual_id": "121"},
        )

    assert response.status_code == 502
    error = response.json()["error"]
    assert error["code"] == "external_service_error"
    assert "quota" in error["message"]


def test_get_models(client):
    """Return the configured model names."""
    response = client.get("/get-models")
    assert response.status_code == 200
    assert response.json() == {
        "chatbot": "gpt-4o-mini",
        "embeddings": "text-embedding-3-small",
    }
