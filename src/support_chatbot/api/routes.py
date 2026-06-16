"""FastAPI routes for chat, admin, and health endpoints."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from support_chatbot.api.dependencies import (
    get_chat_service,
    get_ingestion_service,
    get_settings,
    require_read_key,
    require_write_key,
)
from support_chatbot.api.schemas import (
    IngestManualResponse,
    ModelsResponse,
    QuestionRequest,
    QuestionResponse,
)
from support_chatbot.domain.models import AskRequest, IngestManualRequest
from support_chatbot.settings import AppSettings

router = APIRouter()


@router.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    """Redirect the root path to the interactive API docs."""
    return RedirectResponse(url="/docs")


@router.post("/ask", response_model=QuestionResponse, tags=["chat"])
async def ask_question(
    payload: QuestionRequest,
    request: Request,
    _: None = Depends(require_read_key),
    chat_service=Depends(get_chat_service),
) -> QuestionResponse:
    """Ask the chatbot a question and return the generated answer."""
    client_host = request.client.host if request.client else "unknown"
    result = chat_service.ask(
        AskRequest(
            question=payload.question,
            thread_id=client_host,
            manual_id=payload.manual_id,
        )
    )
    return QuestionResponse(answer=result.answer)


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
    return ModelsResponse(chatbot=settings.model_chat, embeddings=settings.model_embeddings)


@router.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Return a simple health-check response."""
    return {"status": "ok"}
