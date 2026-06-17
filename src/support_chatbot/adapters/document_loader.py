"""Docling-based document loader and splitter adapter."""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from langchain_docling.loader import DoclingLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from support_chatbot.domain.models import Document, ManualConfig
from support_chatbot.domain.ports import DocumentLoader


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
        seen = {stripped for line in doc.page_content.splitlines() if (stripped := line.strip())}
        for line in seen:
            line_doc_counts[line] = line_doc_counts.get(line, 0) + 1

    cutoff = threshold * len(docs)
    boilerplate = {line for line, count in line_doc_counts.items() if count >= cutoff}
    if not boilerplate:
        return docs

    for doc in docs:
        kept = [line for line in doc.page_content.splitlines() if line.strip() not in boilerplate]
        doc.page_content = _collapse_blank_lines("\n".join(kept))

    return docs


def _collapse_blank_lines(text: str) -> str:
    """Collapse runs of blank or whitespace-only lines into one blank line and trim ends."""
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


def _is_allowed_manual_url(url: str, base_url: str, exclude_dirs: tuple[str, ...]) -> bool:
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


@dataclass
class DoclingDocumentLoader(DocumentLoader):
    """Crawl manuals with httpx/BeautifulSoup and convert pages via Docling."""

    export_type: str = "markdown"
    max_pages: int = 500

    def load(self, config: ManualConfig) -> list[Document]:
        """Crawl the manual, convert each page, and strip boilerplate links."""
        urls = _crawl_manual_urls(
            config.root_url,
            config.base_url,
            config.exclude_dirs,
            self.max_pages,
        )
        docs = DoclingLoader(file_path=urls, export_type=self.export_type).load()
        domain_docs = [
            Document(page_content=doc.page_content, metadata=dict(doc.metadata or {}))
            for doc in docs
        ]
        domain_docs = strip_relative_paths(domain_docs)
        if config.strip_boilerplate:
            domain_docs = strip_shared_boilerplate(domain_docs, config.boilerplate_threshold)
        return domain_docs

    def split(self, docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
        """Split documents into overlapping chunks with start-index metadata."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
        )
        chunks = splitter.split_documents(docs)
        return [
            Document(page_content=chunk.page_content, metadata=dict(chunk.metadata or {}))
            for chunk in chunks
        ]
