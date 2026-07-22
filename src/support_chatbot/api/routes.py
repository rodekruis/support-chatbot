"""FastAPI routes for chat, admin, and health endpoints."""

import json
import logging
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, StreamingResponse

from support_chatbot.api.dependencies import (
    get_chat_service,
    get_ingestion_service,
    get_settings,
    require_read_key,
    require_write_key,
)
from support_chatbot.api.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    IngestManualResponse,
    ModelsResponse,
    QuestionRequest,
    QuestionResponse,
    Source,
)
from support_chatbot.domain.models import (
    AnswerComplete,
    AnswerToken,
    AskRequest,
    IngestManualRequest,
)
from support_chatbot.domain.models import (
    FeedbackRequest as FeedbackCommand,
)
from support_chatbot.settings import AppSettings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    """Redirect the root path to the interactive API docs."""
    return RedirectResponse(url="/docs")


@router.post("/ask", response_model=QuestionResponse, tags=["chat"])
async def ask_question(
    payload: QuestionRequest,
    _: None = Depends(require_read_key),
    chat_service=Depends(get_chat_service),
) -> QuestionResponse:
    """Ask the chatbot a question and return the generated answer."""
    session_id = payload.session_id or str(uuid.uuid4())
    result = chat_service.ask(
        AskRequest(
            question=payload.question,
            session_id=session_id,
            manual_id=payload.manual_id,
            user_id=payload.user_id,
        )
    )
    return QuestionResponse(
        answer=result.answer,
        trace_id=result.trace_id,
        sources=[
            Source(url=source.url, title=source.title, score=source.score)
            for source in result.sources
        ],
    )


@router.post("/ask/stream", tags=["chat"])
async def ask_question_stream(
    payload: QuestionRequest,
    _: None = Depends(require_read_key),
    chat_service=Depends(get_chat_service),
) -> StreamingResponse:
    """Stream the answer as newline-delimited JSON (NDJSON) events.

    Each line is one JSON object: ``{"type": "token", "text": ...}`` for answer
    fragments, a final ``{"type": "done", "trace_id": ..., "sources": [...]}``,
    or ``{"type": "error", "message": ...}`` if generation fails mid-stream.
    """
    session_id = payload.session_id or str(uuid.uuid4())
    request = AskRequest(
        question=payload.question,
        session_id=session_id,
        manual_id=payload.manual_id,
        user_id=payload.user_id,
    )

    def event_stream():
        try:
            for event in chat_service.stream(request):
                if isinstance(event, AnswerToken):
                    yield json.dumps({"type": "token", "text": event.text}) + "\n"
                elif isinstance(event, AnswerComplete):
                    yield json.dumps(
                        {
                            "type": "done",
                            "trace_id": event.trace_id,
                            "sources": [
                                {
                                    "url": source.url,
                                    "title": source.title,
                                    "score": source.score,
                                }
                                for source in event.sources
                            ],
                        }
                    ) + "\n"
        except Exception:
            # Once streaming has started the HTTP status is already 200, so
            # surface failures as an in-band error event instead of a 5xx.
            logger.exception("Streaming answer failed")
            yield json.dumps(
                {"type": "error", "message": "answer_generation_failed"}
            ) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=202,
    tags=["chat"],
)
async def submit_feedback(
    payload: FeedbackRequest,
    _: None = Depends(require_read_key),
    chat_service=Depends(get_chat_service),
) -> FeedbackResponse:
    """Attach a thumbs up/down score to a previously generated answer."""
    chat_service.submit_feedback(
        FeedbackCommand(
            trace_id=payload.trace_id,
            positive=payload.positive,
            comment=payload.comment,
        )
    )
    return FeedbackResponse(message="Feedback accepted.")


@router.post(
    "/ingest-manual",
    response_model=IngestManualResponse,
    tags=["admin"],
)
async def ingest_manual(
    manual_id: str,
    _: None = Depends(require_write_key),
    ingestion_service=Depends(get_ingestion_service),
) -> IngestManualResponse:
    """Rebuild the vector store from the configured manual."""
    result = ingestion_service.ingest(IngestManualRequest(manual_id=manual_id))
    return IngestManualResponse(
        message="Vector store successfully updated.",
        documents_indexed=result.documents_indexed,
        index_name=result.index_name,
    )


@router.get("/get-models", response_model=ModelsResponse, tags=["system"])
async def get_models(settings: AppSettings = Depends(get_settings)) -> ModelsResponse:
    """Return the configured chat and embedding model names."""
    return ModelsResponse(
        chatbot=settings.model_chat, embeddings=settings.model_embeddings
    )


@router.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return a simple health-check response."""
    return {"status": "ok"}
