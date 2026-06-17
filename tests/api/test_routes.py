"""API route tests for support_chatbot."""


def test_ask_requires_read_key(client):
    """Reject chat requests without the read API key."""
    response = client.post("/ask", json={"question": "hello", "manual_id": "121"})
    assert response.status_code == 401


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


def test_get_models(client):
    """Return the configured model names."""
    response = client.get("/get-models")
    assert response.status_code == 200
    assert response.json() == {
        "chatbot": "gpt-4o-mini",
        "embeddings": "text-embedding-3-small",
    }
