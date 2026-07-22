"""Domain ports: abstract interfaces implemented by infrastructure adapters.

These protocols decouple the services from concrete infrastructure (for
example Azure AI Search), so the vector database is only ever accessed
through stable, domain-defined interfaces.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from support_chatbot.domain.models import AskResponse, Document, ManualConfig


@runtime_checkable
class DocumentLoader(Protocol):
    """Loads a manual's pages as documents and splits them into chunks."""

    def load(self, config: ManualConfig) -> list[Document]:
        """Crawl the manual described by ``config`` and return its pages."""
        ...

    def split(
        self, docs: list[Document], chunk_size: int, chunk_overlap: int
    ) -> list[Document]:
        """Split documents into overlapping chunks of ``chunk_size``."""
        ...


@runtime_checkable
class VectorStore(Protocol):
    """A per-manual collection of embedded documents."""

    def add_documents(self, docs: list[Document]) -> None:
        """Embed and index a batch of documents."""
        ...

    def similarity_search(self, query: str, k: int = 10) -> list[Document]:
        """Return the ``k`` documents most similar to ``query``."""
        ...

    def similarity_search_with_score(
        self, query: str, k: int = 10
    ) -> list[tuple[Document, float]]:
        """Return the ``k`` most similar documents paired with their relevance score."""
        ...


@runtime_checkable
class VectorStoreProvider(Protocol):
    """Factory and lifecycle manager for per-manual vector stores."""

    def index_name(self, manual_id: str) -> str:
        """Return the backing index name for a manual."""
        ...

    def get_store(self, manual_id: str) -> VectorStore:
        """Return the vector store for a manual, creating it if needed."""
        ...

    def delete_index(self, manual_id: str) -> None:
        """Delete the backing index for a manual."""
        ...


@runtime_checkable
class PromptProvider(Protocol):
    """Supplies the system prompts used to steer the language model.

    Isolates the services and adapter layers from where prompts actually live
    (e.g. a prompt-management backend), so prompt text can change without a
    redeploy and without any framework specifics leaking into the core.
    """

    def get_product_prompt(self, product: str) -> str:
        """Return the product-specific system prompt for a product id."""
        ...

    def get_citation_prompt(self) -> str:
        """Return the product-agnostic prompt used to add inline citations."""
        ...


@runtime_checkable
class ConversationEngine(Protocol):
    """Generates an answer for a question using retrieval and a language model.

    This isolates the services layer from the concrete LLM / orchestration
    framework (LangChain, LangGraph), which lives entirely in an adapter.
    """

    def answer(
        self,
        *,
        question: str,
        session_id: str,
        manual_id: str,
        system_prompt: str,
        user_id: str | None = None,
    ) -> AskResponse:
        """Return the assistant's reply (with an optional trace id) for a question."""
        ...

    def score(
        self,
        *,
        trace_id: str,
        value: float,
        comment: str | None = None,
    ) -> None:
        """Attach a user-feedback score to a previously generated answer.

        Silently ignored by implementations that have no tracing backend
        configured to record the score against.
        """
        ...

    def flush(self) -> None:
        """Flush any pending telemetry before shutdown (no-op if unused)."""
        ...
