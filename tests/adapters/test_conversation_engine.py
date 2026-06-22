"""Unit tests for the conversation engine source extraction."""

from types import SimpleNamespace

from openai import OpenAIError

from support_chatbot.adapters.conversation_engine import LangGraphConversationEngine
from support_chatbot.domain.models import Document


def _tool_message(docs: list[Document]) -> SimpleNamespace:
    return SimpleNamespace(type="tool", artifact=docs)


def _ai_message() -> SimpleNamespace:
    return SimpleNamespace(type="ai", artifact=None)


def _human_message() -> SimpleNamespace:
    return SimpleNamespace(type="human", artifact=None)


def test_extract_sources_returns_current_turn_pages_in_rank_order():
    """Collect retrieved pages from the latest turn, preserving rank."""
    docs = [
        Document(page_content="a", metadata={"source": "https://m/a", "score": 0.9}),
        Document(page_content="b", metadata={"source": "https://m/b", "score": 0.5}),
    ]
    messages = [
        _human_message(),
        _ai_message(),
        _tool_message(docs),
        _ai_message(),
    ]

    sources = LangGraphConversationEngine._extract_sources(messages)

    assert [s.url for s in sources] == ["https://m/a", "https://m/b"]
    assert [s.score for s in sources] == [0.9, 0.5]


def test_extract_sources_deduplicates_by_url():
    """Drop duplicate pages, keeping the first occurrence."""
    docs = [
        Document(page_content="a", metadata={"source": "https://m/a"}),
        Document(page_content="a2", metadata={"source": "https://m/a"}),
    ]
    sources = LangGraphConversationEngine._extract_sources([_tool_message(docs)])

    assert [s.url for s in sources] == ["https://m/a"]


def test_extract_sources_ignores_previous_turns():
    """Only the final contiguous tool block contributes sources."""
    old = [Document(page_content="old", metadata={"source": "https://m/old"})]
    new = [Document(page_content="new", metadata={"source": "https://m/new"})]
    messages = [
        _tool_message(old),
        _ai_message(),
        _human_message(),
        _ai_message(),
        _tool_message(new),
        _ai_message(),
    ]

    sources = LangGraphConversationEngine._extract_sources(messages)

    assert [s.url for s in sources] == ["https://m/new"]


def test_extract_sources_empty_without_tool_messages():
    """Return no sources when the turn used no retrieval."""
    messages = [_human_message(), _ai_message()]

    assert LangGraphConversationEngine._extract_sources(messages) == ()


def test_validate_citation_markers_drops_out_of_range():
    """Strip markers that point past the available sources."""
    text = "First claim [1] and second [3] and third [2]."
    cleaned = LangGraphConversationEngine._validate_citation_markers(
        text, num_sources=2
    )

    assert cleaned == "First claim [1] and second and third [2]."


def test_validate_citation_markers_ignores_years():
    """Leave bracketed multi-digit tokens like years untouched."""
    text = "Released in [2024] and supported [1]."
    cleaned = LangGraphConversationEngine._validate_citation_markers(
        text, num_sources=1
    )

    assert cleaned == "Released in [2024] and supported [1]."


def test_strip_markers_removes_markers_and_normalizes_whitespace():
    """Stripping markers yields the bare normalized text."""
    assert (
        LangGraphConversationEngine._strip_markers("A claim [1] here [2].")
        == "A claim here."
    )


def _engine_with_fake_llm(reply: str | Exception) -> LangGraphConversationEngine:
    """Build an engine instance with a stubbed LLM, bypassing __init__."""
    engine = object.__new__(LangGraphConversationEngine)
    engine._citation_prompt = "cite"

    class _FakeLLM:
        def invoke(self, _messages):
            if isinstance(reply, Exception):
                raise reply
            return SimpleNamespace(content=reply)

    engine._llm = _FakeLLM()
    return engine


def test_add_citations_inserts_valid_markers():
    """Return the annotated answer when the model only inserts markers."""
    engine = _engine_with_fake_llm("The sky is blue [1].")
    docs = [Document(page_content="sky info", metadata={"source": "https://m/a"})]

    result = engine._add_citations("The sky is blue.", docs)

    assert result == "The sky is blue [1]."


def test_add_citations_falls_back_when_wording_changes():
    """Discard a citation response that reworded the answer."""
    engine = _engine_with_fake_llm("Here is the answer: the sky is blue [1].")
    docs = [Document(page_content="sky info", metadata={"source": "https://m/a"})]

    assert engine._add_citations("The sky is blue.", docs) is None


def test_add_citations_falls_back_on_llm_error():
    """Fail open to the plain answer when the citation call raises."""
    engine = _engine_with_fake_llm(OpenAIError("boom"))
    docs = [Document(page_content="sky info", metadata={"source": "https://m/a"})]

    assert engine._add_citations("The sky is blue.", docs) is None
