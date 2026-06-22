"""Unit tests for the conversation engine source extraction."""

from types import SimpleNamespace

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
