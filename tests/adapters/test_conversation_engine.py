"""Unit tests for the conversation engine source extraction."""

from langchain_core.messages import HumanMessage
from openai import OpenAIError

from support_chatbot.adapters.conversation_engine import LangGraphConversationEngine
from support_chatbot.domain.models import Document


def test_extract_sources_returns_pages_in_rank_order():
    """Map retrieved docs to sources, preserving rank and scores."""
    docs = [
        Document(page_content="a", metadata={"source": "https://m/a", "score": 0.9}),
        Document(page_content="b", metadata={"source": "https://m/b", "score": 0.5}),
    ]

    sources = LangGraphConversationEngine._extract_sources(docs)

    assert [s.url for s in sources] == ["https://m/a", "https://m/b"]
    assert [s.score for s in sources] == [0.9, 0.5]


def test_extract_sources_skips_docs_without_url():
    """Drop retrieved docs that have no source URL."""
    docs = [
        Document(page_content="a", metadata={"source": "https://m/a"}),
        Document(page_content="b", metadata={}),
    ]

    sources = LangGraphConversationEngine._extract_sources(docs)

    assert [s.url for s in sources] == ["https://m/a"]


def test_extract_sources_empty_without_docs():
    """Return no sources when nothing was retrieved."""
    assert LangGraphConversationEngine._extract_sources([]) == ()


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


def test_parse_route_detects_direct():
    """A 'direct' router reply routes to the no-retrieval branch."""
    assert LangGraphConversationEngine._parse_route("direct") == "direct"
    assert LangGraphConversationEngine._parse_route(" Direct.\n") == "direct"


def test_parse_route_defaults_to_retrieve():
    """Anything not clearly 'direct' defaults to retrieval (bias toward retrieve)."""
    assert LangGraphConversationEngine._parse_route("retrieve") == "retrieve"
    assert LangGraphConversationEngine._parse_route("") == "retrieve"
    assert LangGraphConversationEngine._parse_route("unsure, maybe direct") == "retrieve"


def test_classify_route_falls_back_to_retrieve_on_router_error():
    """A failed/slow router call defaults to retrieval instead of raising."""
    engine = object.__new__(LangGraphConversationEngine)

    class _FailingLLM:
        def invoke(self, _prompt):
            raise OpenAIError("shared-capacity stall")

    engine._router_llm = _FailingLLM()

    route = engine._classify_route([HumanMessage(content="How do I import beneficiaries?")])

    assert route == "retrieve"


def test_answer_metadata_gates_context_on_retrieval():
    """retrieved_context and search_query are exposed only on retrieval turns."""
    engine = LangGraphConversationEngine.__new__(LangGraphConversationEngine)
    docs = [Document(page_content="a", metadata={"source": "https://m/a"})]

    retrieved = engine._answer_metadata("retrieve", docs, "how do I import from excel?")
    assert retrieved["retrieval_used"] is True
    assert "[1] a" in retrieved["retrieved_context"]
    assert retrieved["search_query"] == "how do I import from excel?"

    direct = engine._answer_metadata("direct", docs, None)
    assert direct["retrieval_used"] is False
    assert "retrieved_context" not in direct
    assert "search_query" not in direct


def test_answer_metadata_history_excludes_current_turn_and_context():
    """conversation_history holds prior Q&A turns only, without retrieved context."""
    from types import SimpleNamespace

    engine = LangGraphConversationEngine.__new__(LangGraphConversationEngine)
    messages = [
        SimpleNamespace(type="human", content="how do I import from excel?"),
        SimpleNamespace(type="ai", content="Use the CSV template. [1]"),
        SimpleNamespace(type="human", content="are you sure?"),
        SimpleNamespace(type="ai", content="Yes, that's correct."),
    ]

    metadata = engine._answer_metadata("direct", [], None, messages)

    assert metadata["conversation_history"] == (
        "user: how do I import from excel?\nassistant: Use the CSV template. [1]"
    )
    # the current turn is recorded separately (input/output), not in history
    assert "are you sure?" not in metadata["conversation_history"]


def test_format_history_empty_on_first_turn():
    """A first turn (only the current exchange) yields empty history."""
    from types import SimpleNamespace

    messages = [
        SimpleNamespace(type="human", content="hello"),
        SimpleNamespace(type="ai", content="Hi there!"),
    ]

    assert LangGraphConversationEngine._format_history(messages) == ""

