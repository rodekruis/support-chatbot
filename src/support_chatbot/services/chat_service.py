"""Chat orchestration service for manual question answering."""

from __future__ import annotations

from support_chatbot.domain.models import AskRequest, AskResponse, FeedbackRequest
from support_chatbot.domain.ports import ConversationEngine, PromptProvider


class ChatService:
    """Coordinate prompt loading and delegate answering to a conversation engine."""

    def __init__(self, engine: ConversationEngine, prompts: PromptProvider) -> None:
        """Initialize with the conversation engine and prompt provider."""
        self._engine = engine
        self._prompts = prompts

    def ask(self, request: AskRequest) -> AskResponse:
        """Ask the chatbot a question and return the final assistant reply."""
        system_prompt = self._prompts.get_product_prompt(request.manual_id)
        return self._engine.answer(
            question=request.question,
            session_id=request.session_id,
            manual_id=request.manual_id,
            system_prompt=system_prompt,
            user_id=request.user_id,
        )

    def submit_feedback(self, request: FeedbackRequest) -> None:
        """Record thumbs up/down feedback against a previously generated answer."""
        self._engine.score(
            trace_id=request.trace_id,
            value=1.0 if request.positive else 0.0,
            comment=request.comment,
        )
