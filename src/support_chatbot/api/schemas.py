from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, description="Text of the user question.")


class QuestionResponse(BaseModel):
    answer: str


class UpdateVectorStoreResponse(BaseModel):
    message: str
    documents_indexed: int
    index_name: str


class ModelsResponse(BaseModel):
    chatbot: str
    embeddings: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
