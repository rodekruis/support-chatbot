from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from support_chatbot.api.dependencies import (
    get_chat_service,
    get_settings,
    get_vector_store_service,
    require_read_key,
    require_write_key,
)
from support_chatbot.api.schemas import (
    ModelsResponse,
    QuestionRequest,
    QuestionResponse,
    UpdateVectorStoreResponse,
)
from support_chatbot.settings import AppSettings

router = APIRouter()


@router.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@router.post("/ask", response_model=QuestionResponse, tags=["chat"])
async def ask_question(
    payload: QuestionRequest,
    request: Request,
    _: None = Depends(require_read_key),
    chat_service=Depends(get_chat_service),
) -> QuestionResponse:
    client_host = request.client.host if request.client else "unknown"
    answer = chat_service.ask(payload.question, thread_id=client_host)
    return QuestionResponse(answer=answer)


@router.post(
    "/update-vector-store",
    response_model=UpdateVectorStoreResponse,
    tags=["admin"],
)
async def update_vector_store(
    _: None = Depends(require_write_key),
    vector_store_service=Depends(get_vector_store_service),
    settings: AppSettings = Depends(get_settings),
) -> UpdateVectorStoreResponse:
    documents_indexed = vector_store_service.update_from_manual()
    return UpdateVectorStoreResponse(
        message="Vector store successfully updated.",
        documents_indexed=documents_indexed,
        index_name=settings.vector_store_id,
    )


@router.get("/get-models", response_model=ModelsResponse, tags=["system"])
async def get_models(settings: AppSettings = Depends(get_settings)) -> ModelsResponse:
    return ModelsResponse(
        chatbot=settings.model_chat, embeddings=settings.model_embeddings
    )


@router.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
