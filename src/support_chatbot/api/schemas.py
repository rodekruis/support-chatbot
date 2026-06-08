"""Pydantic models used by the public API."""

from pydantic import BaseModel, Field

from support_chatbot.config.manuals import DEFAULT_MANUAL_ID


class QuestionRequest(BaseModel):
    """Request body for asking a question about a manual."""

    question: str = Field(min_length=1, description="Text of the user question.")
    manual_id: str = Field(
        default=DEFAULT_MANUAL_ID,
        description="Id of the manual to answer from.",
    )


class QuestionResponse(BaseModel):
    """Response body containing the chatbot answer."""

    answer: str


class UpdateVectorStoreResponse(BaseModel):
    """Response body for vector store refresh requests."""

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
