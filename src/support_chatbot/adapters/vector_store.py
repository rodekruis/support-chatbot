from __future__ import annotations

from dataclasses import dataclass

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings

from support_chatbot.settings import AppSettings


@dataclass
class VectorStoreBundle:
    vector_store: AzureSearch
    index_client: SearchIndexClient


def build_vector_store_bundle(settings: AppSettings) -> VectorStoreBundle:
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key.get_secret_value(),
        api_version=settings.azure_openai_api_version,
        deployment=settings.model_embeddings,
        chunk_size=1,
    )

    vector_store = AzureSearch(
        azure_search_endpoint=settings.vector_store_address,
        azure_search_key=settings.vector_store_password.get_secret_value(),
        index_name=settings.vector_store_id,
        embedding_function=embeddings.embed_query,
    )

    index_client = SearchIndexClient(
        settings.vector_store_address,
        AzureKeyCredential(settings.vector_store_password.get_secret_value()),
    )

    return VectorStoreBundle(vector_store=vector_store, index_client=index_client)
