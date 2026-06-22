"""Kreuzberg-based document loader and splitter adapter."""

from __future__ import annotations

import logging
import re
from collections import deque
from dataclasses import dataclass
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from kreuzberg import ExtractionConfig, extract_bytes_sync
from langchain_text_splitters import RecursiveCharacterTextSplitter

from support_chatbot.domain.models import Document, ManualConfig
from support_chatbot.domain.ports import DocumentLoader

logger = logging.getLogger(__name__)


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


def _preprocess_html(html: str) -> str:
    """Replace permission icon spans with text so their meaning survives conversion.

    The manual encodes permission availability as inline ``<svg>`` icons inside
    ``<span class="twemoji yes">`` (feature available) and
    ``<span class="twemoji req">`` (available on request). The meaning lives only
    in the CSS class, so every markdown converter drops it. Replacing the spans
    with plain text before extraction preserves the permission matrix.
    """
    soup = BeautifulSoup(html, "html.parser")
    for span in soup.select("span.twemoji.yes"):
        span.replace_with("Yes")
    for span in soup.select("span.twemoji.req"):
        span.replace_with("On request")
    return str(soup)


def _normalize_url(url: str) -> str:
    return urldefrag(url).url


def _split_table_row(row: str) -> list[str]:
    """Split a markdown table row into its cells, dropping the outer pipes."""
    return row.strip().strip("|").split("|")


def _has_mostly_empty_table(
    markdown: str, min_cells: int = 10, min_fill_ratio: float = 0.15
) -> bool:
    """Return True if any markdown table has almost no real text in its value cells.

    Detects the failure mode where a whole column of meaningful content (such as
    icon-encoded markers) is lost during conversion. Cells that contain only an
    image (e.g. an inline ``![SVG Image](data:...)`` blob) or nothing are treated
    as empty, since neither carries extractable text. Only tables with at least
    ``min_cells`` value cells are checked, so small or legitimately sparse tables
    are not flagged.
    """
    separator = re.compile(r"^:?-+:?$")
    image = re.compile(r"!\[[^\]]*\]\([^)]*\)")

    def _cell_text(cell: str) -> str:
        return image.sub("", cell).strip()

    def _is_mostly_empty(block: list[str]) -> bool:
        data_rows = [
            row
            for row in block
            if not all(separator.match(c.strip()) for c in _split_table_row(row))
        ]
        # Drop the header row; keep value cells, excluding the first label column.
        value_cells = [
            _cell_text(c) for row in data_rows[1:] for c in _split_table_row(row)[1:]
        ]
        if len(value_cells) < min_cells:
            return False
        filled = sum(1 for c in value_cells if c)
        return filled / len(value_cells) < min_fill_ratio

    block: list[str] = []
    for line in [*markdown.splitlines(), ""]:
        stripped = line.strip()
        if stripped.startswith("|"):
            block.append(stripped)
            continue
        if block:
            if _is_mostly_empty(block):
                return True
            block = []
    return False


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


@dataclass
class KreuzbergDocumentLoader(DocumentLoader):
    """Crawl manuals with httpx/BeautifulSoup and convert pages via Kreuzberg."""

    max_pages: int = 500

    def load(self, config: ManualConfig) -> list[Document]:
        """Crawl the manual, convert each page, and strip boilerplate links."""
        urls = _crawl_manual_urls(
            config.root_url,
            config.base_url,
            config.exclude_dirs,
            self.max_pages,
        )
        extraction_config = ExtractionConfig(output_format="markdown")
        domain_docs: list[Document] = []
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            for url in urls:
                try:
                    response = client.get(url)
                    response.raise_for_status()
                except Exception:
                    continue

                mime_type = (
                    response.headers.get("content-type", "text/html")
                    .split(";")[0]
                    .strip()
                    or "text/html"
                )
                if mime_type == "text/html":
                    content = _preprocess_html(response.text).encode("utf-8")
                else:
                    content = response.content
                try:
                    result = extract_bytes_sync(
                        content, mime_type, config=extraction_config
                    )
                except Exception:
                    continue

                if mime_type == "text/html" and _has_mostly_empty_table(result.content):
                    logger.warning(
                        "Skipping page with mostly-empty table, indicating dropped "
                        "content (e.g. icon-encoded cells)",
                        extra={"source": url},
                    )
                    continue

                domain_docs.append(
                    Document(page_content=result.content, metadata={"source": url})
                )

        domain_docs = strip_relative_paths(domain_docs)
        if config.strip_boilerplate:
            domain_docs = strip_shared_boilerplate(
                domain_docs, config.boilerplate_threshold
            )
        return domain_docs

    def split(
        self, docs: list[Document], chunk_size: int, chunk_overlap: int
    ) -> list[Document]:
        """Split documents into overlapping chunks with start-index metadata."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
        )
        chunks = splitter.split_documents(docs)
        return [
            Document(
                page_content=chunk.page_content, metadata=dict(chunk.metadata or {})
            )
            for chunk in chunks
        ]
