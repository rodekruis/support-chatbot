"""Unit tests for the ChatService orchestration layer."""

from collections.abc import Iterator

from support_chatbot.domain.models import (
    AnswerComplete,
    AnswerToken,
    AskRequest,
    AskResponse,
    FeedbackRequest,
)
from support_chatbot.services.chat_service import ChatService


class FakePromptProvider:
    """Prompt provider double returning predictable prompt text."""

    def get_product_prompt(self, product: str) -> str:
        """Return a product-tagged system prompt for assertions."""
        return f"prompt:{product}"

    def get_citation_prompt(self) -> str:
        """Return a placeholder citation prompt."""
        return "cite"

    def get_direct_answer_prompt(self) -> str:
        """Return a placeholder direct-answer prompt."""
        return "direct"


class FakeEngine:
    """Conversation engine double that records how it was called."""

    def __init__(self) -> None:
        """Initialize per-method call logs."""
        self.answer_calls: list[dict] = []
        self.stream_calls: list[dict] = []
        self.score_calls: list[dict] = []

    def answer(
        self, *, question, session_id, manual_id, system_prompt, user_id=None
    ) -> AskResponse:
        """Record the call and echo the question as the answer."""
        self.answer_calls.append(
            {
                "question": question,
                "session_id": session_id,
                "manual_id": manual_id,
                "system_prompt": system_prompt,
                "user_id": user_id,
            }
        )
        return AskResponse(answer=f"answer:{question}", trace_id="t1")

    def stream(
        self, *, question, session_id, manual_id, system_prompt, user_id=None
    ) -> Iterator[AnswerToken | AnswerComplete]:
        """Record the call and yield a token then a completion event."""
        self.stream_calls.append(
            {"system_prompt": system_prompt, "manual_id": manual_id}
        )
        yield AnswerToken(text=question)
        yield AnswerComplete(trace_id="t1")

    def score(self, *, trace_id, value, comment=None) -> None:
        """Record a feedback score call."""
        self.score_calls.append(
            {"trace_id": trace_id, "value": value, "comment": comment}
        )


def _service() -> tuple[ChatService, FakeEngine]:
    engine = FakeEngine()
    return ChatService(engine, FakePromptProvider()), engine


def test_ask_injects_product_prompt_and_forwards_request():
    """ask() loads the manual's prompt and forwards every field to the engine."""
    service, engine = _service()

    result = service.ask(
        AskRequest(question="how?", session_id="s1", manual_id="121", user_id="u1")
    )

    assert result.answer == "answer:how?"
    assert engine.answer_calls == [
        {
            "question": "how?",
            "session_id": "s1",
            "manual_id": "121",
            "system_prompt": "prompt:121",
            "user_id": "u1",
        }
    ]


def test_stream_injects_product_prompt_and_delegates():
    """stream() loads the manual's prompt and relays the engine's events."""
    service, engine = _service()

    events = list(
        service.stream(AskRequest(question="hi", session_id="s1", manual_id="121"))
    )

    assert engine.stream_calls[0]["system_prompt"] == "prompt:121"
    assert isinstance(events[0], AnswerToken)
    assert isinstance(events[-1], AnswerComplete)


def test_submit_feedback_maps_thumbs_to_numeric_score():
    """submit_feedback() maps thumbs up/down to 1.0/0.0 and forwards the comment."""
    service, engine = _service()

    service.submit_feedback(
        FeedbackRequest(trace_id="t1", positive=True, comment="great")
    )
    service.submit_feedback(FeedbackRequest(trace_id="t2", positive=False))

    assert engine.score_calls == [
        {"trace_id": "t1", "value": 1.0, "comment": "great"},
        {"trace_id": "t2", "value": 0.0, "comment": None},
    ]
