"""Chat orchestration service for manual question answering."""

from __future__ import annotations

from support_chatbot.config.manuals import get_manual_prompt
from support_chatbot.domain.models import AskRequest, AskResponse, FeedbackRequest
from support_chatbot.domain.ports import ConversationEngine


class ChatService:
    """Coordinate prompt loading and delegate answering to a conversation engine."""

    def __init__(self, engine: ConversationEngine) -> None:
        """Initialize with the conversation engine used to generate answers."""
        self._engine = engine
        self._prompt_cache: dict[str, str] = {}

    def _get_prompt(self, manual_id: str) -> str:
        if manual_id not in self._prompt_cache:
            self._prompt_cache[manual_id] = get_manual_prompt(manual_id)
        return self._prompt_cache[manual_id]

    def ask(self, request: AskRequest) -> AskResponse:
        """Ask the chatbot a question and return the final assistant reply."""
        system_prompt = self._get_prompt(request.manual_id)
        return self._engine.answer(
            question=request.question,
            thread_id=request.thread_id,
            manual_id=request.manual_id,
            system_prompt=system_prompt,
        )

    def submit_feedback(self, request: FeedbackRequest) -> None:
        """Record thumbs up/down feedback against a previously generated answer."""
        self._engine.score(
            trace_id=request.trace_id,
            value=1.0 if request.positive else 0.0,
            comment=request.comment,
        )
