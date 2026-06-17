"""Application service that crawls a manual and indexes its pages via the vector store port."""

from __future__ import annotations

from typing import TYPE_CHECKING

from support_chatbot.config.manuals import get_manual_config
from support_chatbot.domain.models import IngestManualRequest, IngestManualResponse

if TYPE_CHECKING:
    from support_chatbot.domain.ports import DocumentLoader, VectorStoreProvider
    from support_chatbot.settings import AppSettings


class ManualIngestionService:
    """Crawl a manual, convert its pages to documents, and index them in the vector store."""

    def __init__(
        self,
        settings: AppSettings,
        provider: VectorStoreProvider,
        loader: DocumentLoader,
    ) -> None:
        """Store the dependencies needed to refresh a manual index."""
        self._settings = settings
        self._provider = provider
        self._loader = loader

    def ingest(self, request: IngestManualRequest) -> IngestManualResponse:
        """Refresh the vector store for a manual and return the indexing summary."""
        manual_id = request.manual_id
        manual_config = get_manual_config(manual_id)
        index_name = self._provider.index_name(manual_id)

        docs = self._loader.load(manual_config)

        if manual_config.chunk_size is not None:
            docs = self._loader.split(
                docs,
                manual_config.chunk_size,
                manual_config.chunk_overlap or 0,
            )

        self._provider.delete_index(manual_id)
        self._provider.get_store(manual_id).add_documents(docs)
        return IngestManualResponse(documents_indexed=len(docs), index_name=index_name)
