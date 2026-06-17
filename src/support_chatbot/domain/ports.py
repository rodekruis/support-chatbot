"""Domain ports: abstract interfaces implemented by infrastructure adapters.

These protocols decouple the services from concrete infrastructure (for
example Azure AI Search), so the vector database is only ever accessed
through stable, domain-defined interfaces.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from support_chatbot.domain.models import Document, ManualConfig


@runtime_checkable
class DocumentLoader(Protocol):
    """Loads a manual's pages as documents and splits them into chunks."""

    def load(self, config: ManualConfig) -> list[Document]:
        """Crawl the manual described by ``config`` and return its pages."""
        ...

    def split(self, docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
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
