"""Manual ingestion service for building Azure AI Search indexes."""

from __future__ import annotations

from collections import deque
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from langchain_docling.loader import DoclingLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from support_chatbot.config.manuals import DEFAULT_MANUAL_ID, get_manual_config

if TYPE_CHECKING:
    from support_chatbot.adapters.vector_store import VectorStoreProvider
    from support_chatbot.settings import AppSettings


@dataclass(frozen=True)
class ManualUpdateResult:
    """Summary of a manual indexing run."""

    documents_indexed: int
    index_name: str


def strip_shared_boilerplate(docs: list, threshold: float = 0.9) -> list:
    """Remove lines that are shared across (nearly) all documents in place.

    Navigation menus, logos, headers and footers appear as identical text on
    every page of a manual. By counting how many documents each (stripped,
    non-empty) line appears in and dropping those present in at least
    ``threshold`` fraction of documents, this boilerplate is removed while
    page-specific content is kept.
    """
    if len(docs) < 2:
        return docs

    line_doc_counts: dict[str, int] = {}
    for doc in docs:
        seen = {
            stripped
            for line in doc.page_content.splitlines()
            if (stripped := line.strip())
        }
        for line in seen:
            line_doc_counts[line] = line_doc_counts.get(line, 0) + 1

    cutoff = threshold * len(docs)
    boilerplate = {line for line, count in line_doc_counts.items() if count >= cutoff}
    if not boilerplate:
        return docs

    for doc in docs:
        kept = [
            line
            for line in doc.page_content.splitlines()
            if line.strip() not in boilerplate
        ]
        doc.page_content = _collapse_blank_lines("\n".join(kept))

    return docs


def _collapse_blank_lines(text: str) -> str:
    """Collapse runs of blank lines or lines with only spaces into a single blank line and trim ends."""
    return re.sub(r"\n[^\S\n]*(?:\n[^\S\n]*)+", "\n\n", text).strip()


def strip_relative_paths(docs: list) -> list:
    """Remove non-absolute markdown links and raw relative paths from docs."""
    markdown_link = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    raw_relative_path = re.compile(r"(?<!\w)(?:\.\.?[\\/])(?:[^\s)\]]+)")

    def _strip_non_absolute_links(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()
        if target.lower().startswith(("http://", "https://")):
            return match.group(0)
        return label

    for doc in docs:
        text = markdown_link.sub(_strip_non_absolute_links, doc.page_content)
        text = raw_relative_path.sub("", text)
        doc.page_content = _collapse_blank_lines(text)

    return docs


def _normalize_url(url: str) -> str:
    return urldefrag(url).url


def _is_allowed_manual_url(
    url: str, base_url: str, exclude_dirs: tuple[str, ...]
) -> bool:
    parsed = urlparse(url)
    base_parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if parsed.netloc != base_parsed.netloc:
        return False

    base_path = base_parsed.path.rstrip("/") + "/"
    current_path = parsed.path
    if not (current_path == base_parsed.path or current_path.startswith(base_path)):
        return False

    for excluded in exclude_dirs:
        excluded_normalized = _normalize_url(excluded)
        if url.startswith(excluded_normalized):
            return False

    return True


def _crawl_manual_urls(
    root_url: str,
    base_url: str,
    exclude_dirs: tuple[str, ...],
    max_pages: int = 500,
) -> list[str]:
    """Crawl the manual domain and return in-scope page URLs."""
    queue: deque[str] = deque([_normalize_url(root_url)])
    visited: set[str] = set()
    urls: list[str] = []

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        while queue and len(urls) < max_pages:
            current = _normalize_url(queue.popleft())
            if current in visited:
                continue
            visited.add(current)

            if not _is_allowed_manual_url(current, base_url, exclude_dirs):
                continue

            try:
                response = client.get(current)
                response.raise_for_status()
            except Exception:
                continue

            urls.append(current)
            if "text/html" not in response.headers.get("content-type", "").lower():
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for anchor in soup.select("a[href]"):
                href = anchor.get("href")
                if not href:
                    continue
                candidate = _normalize_url(urljoin(current, href))
                if candidate not in visited and _is_allowed_manual_url(
                    candidate, base_url, exclude_dirs
                ):
                    queue.append(candidate)

    return urls


class VectorStoreService:
    """Crawl a manual, convert its pages, and index the resulting documents."""

    def __init__(
        self,
        settings: AppSettings,
        provider: VectorStoreProvider,
        default_manual_id: str = DEFAULT_MANUAL_ID,
    ) -> None:
        """Store the dependencies needed to refresh a manual index."""
        self._settings = settings
        self._provider = provider
        self._default_manual_id = default_manual_id

    def update_from_manual(self, manual_id: str | None = None) -> ManualUpdateResult:
        """Refresh the vector store for a manual and return the indexing summary."""
        manual_id = manual_id or self._default_manual_id
        manual_config = get_manual_config(manual_id)
        index_name = self._provider.index_name(manual_id)

        urls = _crawl_manual_urls(
            manual_config.root_url,
            manual_config.base_url,
            manual_config.exclude_dirs,
        )
        docs = DoclingLoader(file_path=urls, export_type="markdown").load()
        docs = strip_relative_paths(list(docs))

        if manual_config.strip_boilerplate:
            docs = strip_shared_boilerplate(
                list(docs), manual_config.boilerplate_threshold
            )

        if manual_config.chunk_size is not None:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=manual_config.chunk_size,
                chunk_overlap=manual_config.chunk_overlap or 0,
                add_start_index=True,
            )
            docs = splitter.split_documents(docs)

        self._provider.index_client.delete_index(index_name)
        self._provider.get_store(manual_id).add_documents(docs)
        return ManualUpdateResult(documents_indexed=len(docs), index_name=index_name)
