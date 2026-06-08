def test_ask_requires_read_key(client):
    response = client.post("/ask", json={"question": "hello"})
    assert response.status_code == 401


def test_ask_returns_answer_with_read_key(client):
    response = client.post(
        "/ask",
        headers={"Authorization": "read-key"},
        json={"question": "hello"},
    )
    assert response.status_code == 200
    assert response.json()["answer"].startswith("echo:hello")


def test_update_vector_store_requires_write_key(client):
    response = client.post(
        "/update-vector-store", headers={"Authorization": "read-key"}
    )
    assert response.status_code == 401


def test_update_vector_store_with_write_key(client):
    response = client.post(
        "/update-vector-store", headers={"Authorization": "write-key"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["documents_indexed"] == 3
    assert payload["index_name"] == "support-chatbot-index"


def test_get_models(client):
    response = client.get("/get-models")
    assert response.status_code == 200
    assert response.json() == {
        "chatbot": "gpt-4o-mini",
        "embeddings": "text-embedding-3-small",
    }
