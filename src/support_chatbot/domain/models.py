"""Domain models shared across the application core."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ManualConfig:
    """Configuration for a single manual source and its indexing behavior."""

    manual_id: str
    root_url: str
    base_url: str
    exclude_dirs: tuple[str, ...]
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    strip_boilerplate: bool = True
    boilerplate_threshold: float = 0.9


@dataclass
class Document:
    """A unit of text with associated metadata."""

    page_content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AskRequest:
    """Input for asking the chatbot a question about a manual."""

    question: str
    session_id: str
    manual_id: str
    user_id: str | None = None


@dataclass(frozen=True)
class Source:
    """A manual page that backed an answer, with an optional relevance score."""

    url: str
    title: str | None = None
    score: float | None = None


@dataclass(frozen=True)
class AskResponse:
    """Result of answering a chatbot question."""

    answer: str
    trace_id: str | None = None
    sources: tuple[Source, ...] = ()


@dataclass(frozen=True)
class AnswerToken:
    """A streamed fragment of the assistant's answer text."""

    text: str


@dataclass(frozen=True)
class AnswerComplete:
    """Terminal streaming event carrying the trace id and backing sources."""

    trace_id: str | None = None
    sources: tuple[Source, ...] = ()


@dataclass(frozen=True)
class FeedbackRequest:
    """User feedback (thumbs up/down) on a previously generated answer."""

    trace_id: str
    positive: bool
    comment: str | None = None


@dataclass(frozen=True)
class IngestManualRequest:
    """Input for rebuilding a manual's vector store index."""

    manual_id: str


@dataclass(frozen=True)
class IngestManualResponse:
    """Summary of a manual indexing run."""

    documents_indexed: int
    index_name: str
