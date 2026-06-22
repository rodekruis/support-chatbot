"""Pydantic models used by the public API."""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Request body for asking a question about a manual."""

    question: str = Field(min_length=1, description="Text of the user question.")
    manual_id: str = Field(
        min_length=1,
        description="Id of the manual to answer from.",
    )


class Source(BaseModel):
    """A manual page that backed an answer."""

    url: str = Field(description="Link to the manual page.")
    title: str | None = Field(
        default=None, description="Human-readable page title, when available."
    )
    score: float | None = Field(
        default=None, description="Relevance score reported by the vector store."
    )


class QuestionResponse(BaseModel):
    """Response body containing the chatbot answer."""

    answer: str
    trace_id: str | None = Field(
        default=None,
        description="Observability trace id; pass it back to /feedback to score the answer.",
    )
    sources: list[Source] = Field(
        default_factory=list,
        description="Manual pages that backed the answer, ordered by relevance.",
    )


class FeedbackRequest(BaseModel):
    """Request body for submitting thumbs up/down feedback on an answer."""

    trace_id: str = Field(
        min_length=1,
        description="Trace id returned by /ask for the answer being rated.",
    )
    positive: bool = Field(
        description="True for thumbs up, False for thumbs down.",
    )
    comment: str | None = Field(
        default=None,
        description="Optional free-text feedback.",
    )


class FeedbackResponse(BaseModel):
    """Response body confirming feedback was recorded."""

    message: str


class IngestManualResponse(BaseModel):
    """Response body for manual ingestion requests."""

    message: str
    documents_indexed: int
    index_name: str


class ModelsResponse(BaseModel):
    """Response body listing configured model names."""

    chatbot: str
    embeddings: str


class ErrorDetail(BaseModel):
    """Structured error payload returned by the API."""

    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    """Top-level error response wrapper."""

    error: ErrorDetail
