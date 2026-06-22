"""Unit tests for the Azure vector store adapter query shape."""

from support_chatbot.adapters.vector_store import AzureVectorStore


class _FakeEmbeddings:
    def embed_query(self, _text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class _FakeSearchClient:
    def __init__(self) -> None:
        self.captured: dict | None = None

    def search(self, **kwargs):
        self.captured = kwargs
        return iter(
            [
                {
                    "content": "Reset your password from the login page.",
                    "source": "https://m/reset",
                    "metadata_json": '{"title": "Reset password"}',
                    "@search.score": 0.0312,
                }
            ]
        )


def _build_store(fake_client: _FakeSearchClient) -> AzureVectorStore:
    store = AzureVectorStore(
        endpoint="https://example.search.windows.net",
        api_key="dummy",
        index_name="idx",
        embeddings=_FakeEmbeddings(),
        vector_dimensions=3,
    )
    store._search_client = lambda: fake_client  # type: ignore[method-assign]
    return store


def test_similarity_search_runs_hybrid_query():
    """Send both keyword search_text and a vector query for RRF hybrid search."""
    fake = _FakeSearchClient()
    store = _build_store(fake)

    store.similarity_search_with_score("reset password", k=8)

    assert fake.captured is not None
    assert fake.captured["search_text"] == "reset password"
    assert len(fake.captured["vector_queries"]) == 1
    assert fake.captured["top"] == 8


def test_similarity_search_returns_scored_documents_with_metadata():
    """Map results to documents carrying the fused score and stored metadata."""
    fake = _FakeSearchClient()
    store = _build_store(fake)

    results = store.similarity_search_with_score("reset password", k=8)

    assert len(results) == 1
    doc, score = results[0]
    assert doc.metadata["source"] == "https://m/reset"
    assert doc.metadata["title"] == "Reset password"
    assert score == 0.0312
