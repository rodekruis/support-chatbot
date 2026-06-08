from __future__ import annotations

from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_community.document_transformers import MarkdownifyTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from support_chatbot.settings import AppSettings


class VectorStoreService:
    def __init__(self, settings: AppSettings, vector_store, index_client) -> None:
        self._settings = settings
        self._vector_store = vector_store
        self._index_client = index_client

    def update_from_manual(self) -> int:
        loader = RecursiveUrlLoader(
            "https://manual.121.global/en/",
            prevent_outside=True,
            base_url="https://manual.121.global/en/",
            exclude_dirs=["https://manual.121.global/en/nlrc"],
        )
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        docs = splitter.split_documents(docs)

        markdownifier = MarkdownifyTransformer(strip="a")
        docs = markdownifier.transform_documents(docs)

        self._index_client.delete_index(self._settings.vector_store_id)
        self._vector_store.add_documents(docs)
        return len(docs)
