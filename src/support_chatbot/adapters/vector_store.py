"""Azure AI Search-backed vector store adapter."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from support_chatbot.settings import AppSettings


@dataclass
class AzureVectorStore:
    """Minimal vector store wrapper using Azure AI Search native SDK."""

    endpoint: str
    api_key: str
    index_name: str
    embeddings: AzureOpenAIEmbeddings
    vector_dimensions: int

    def _credential(self) -> AzureKeyCredential:
        return AzureKeyCredential(self.api_key)

    def _index_client(self) -> SearchIndexClient:
        return SearchIndexClient(self.endpoint, self._credential())

    def _search_client(self) -> SearchClient:
        return SearchClient(self.endpoint, self.index_name, self._credential())

    def _ensure_index(self) -> None:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(
                name="source", type=SearchFieldDataType.String, filterable=True
            ),
            SimpleField(name="metadata_json", type=SearchFieldDataType.String),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self.vector_dimensions,
                vector_search_profile_name="default-profile",
            ),
        ]
        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
            profiles=[
                VectorSearchProfile(
                    name="default-profile", algorithm_configuration_name="default-hnsw"
                )
            ],
        )
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
        )
        self._index_client().create_or_update_index(index)

    def add_documents(self, docs: list[Document]) -> None:
        """Index a batch of documents in Azure AI Search."""
        if not docs:
            return

        self._ensure_index()
        contents = [doc.page_content for doc in docs]
        vectors = self.embeddings.embed_documents(contents)

        payload = []
        for doc, vector in zip(docs, vectors, strict=False):
            metadata = doc.metadata or {}
            payload.append(
                {
                    "id": str(uuid.uuid4()),
                    "content": doc.page_content,
                    "source": str(metadata.get("source", "")),
                    "metadata_json": json.dumps(metadata, ensure_ascii=True),
                    "content_vector": vector,
                }
            )

        search_client = self._search_client()
        batch_size = 100
        for i in range(0, len(payload), batch_size):
            search_client.upload_documents(documents=payload[i : i + batch_size])

    def similarity_search(self, query: str, k: int = 10) -> list[Document]:
        """Return the nearest documents for a query string."""
        query_vector = self.embeddings.embed_query(query)
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="content_vector",
        )
        results = self._search_client().search(
            search_text=None,
            vector_queries=[vector_query],
            top=k,
            select=["content", "source", "metadata_json"],
        )

        docs: list[Document] = []
        for result in results:
            metadata = {}
            metadata_json = result.get("metadata_json")
            if metadata_json:
                try:
                    metadata = json.loads(metadata_json)
                except json.JSONDecodeError:
                    metadata = {}
            source = result.get("source")
            if source and "source" not in metadata:
                metadata["source"] = source
            docs.append(
                Document(page_content=result.get("content", ""), metadata=metadata)
            )
        return docs


class VectorStoreProvider:
    """Provides one Azure Search index per manual.

    Each manual is stored in its own index named ``{vector_store_id}-{manual_id}``
    so that retrieval for a given manual only searches that manual's content.
    Stores are created lazily and cached, while embeddings and the index client
    are shared across all manuals.
    """

    def __init__(self, settings: AppSettings) -> None:
        """Create shared embeddings and search clients for manual indexes."""
        self._settings = settings
        self._embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key.get_secret_value(),
            api_version=settings.azure_openai_api_version,
            deployment=settings.model_embeddings,
            chunk_size=1,
        )
        self._embedding_dimensions = len(self._embeddings.embed_query("healthcheck"))
        self._index_client = SearchIndexClient(
            settings.vector_store_address,
            AzureKeyCredential(settings.vector_store_password.get_secret_value()),
        )
        self._stores: dict[str, AzureVectorStore] = {}

    @property
    def index_client(self) -> SearchIndexClient:
        """Return the shared Azure Search index client."""
        return self._index_client

    def index_name(self, manual_id: str) -> str:
        """Return the Azure Search index name for a manual."""
        return f"{self._settings.vector_store_id}-{manual_id}"

    def get_store(self, manual_id: str) -> AzureVectorStore:
        """Return the cached vector store for a manual, creating it if needed."""
        if manual_id not in self._stores:
            self._stores[manual_id] = AzureVectorStore(
                endpoint=self._settings.vector_store_address,
                api_key=self._settings.vector_store_password.get_secret_value(),
                index_name=self.index_name(manual_id),
                embeddings=self._embeddings,
                vector_dimensions=self._embedding_dimensions,
            )
        return self._stores[manual_id]
