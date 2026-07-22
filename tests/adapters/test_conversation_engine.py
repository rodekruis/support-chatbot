"""Unit tests for the conversation engine source extraction."""

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

