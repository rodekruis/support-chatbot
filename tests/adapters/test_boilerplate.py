"""Tests for manual boilerplate stripping helpers."""

from langchain_core.documents import Document

from support_chatbot.adapters.document_loader import strip_shared_boilerplate

SHARED_HEADER = ["121 Platform User Manual", "Skip to content", "* General"]
SHARED_FOOTER = ["Was this page helpful?", "Back to top"]


def _page(title: str, body: list[str]) -> Document:
    content = "\n".join([*SHARED_HEADER, title, *body, *SHARED_FOOTER])
    return Document(page_content=content)


def test_strips_lines_shared_across_all_pages():
    """Remove header and footer lines that appear on every page."""
    docs = [
        _page("Home", ["Welcome to the home page."]),
        _page("Settings", ["Configure your program here."]),
        _page("Users", ["Add and manage users."]),
    ]

    result = strip_shared_boilerplate(docs, threshold=0.9)

    for doc in result:
        for shared in SHARED_HEADER + SHARED_FOOTER:
            assert shared not in doc.page_content

    # Page-specific content and unique titles are kept.
    assert "Welcome to the home page." in result[0].page_content
    assert "Home" in result[0].page_content
    assert "Configure your program here." in result[1].page_content


def test_collapses_blank_lines_left_after_stripping():
    """Collapse blank-line runs that remain after shared text is removed."""
    # Shared lines surrounded by blank lines (as in real markdown) leave gaps
    # once removed; those runs of blanks should collapse to a single blank line.
    docs = [
        Document(
            page_content="\n".join(
                ["SHARED", "", "Intro A", "", "SHARED", "", "Body A", "", "SHARED"]
            )
        ),
        Document(
            page_content="\n".join(
                ["SHARED", "", "Intro B", "", "SHARED", "", "Body B", "", "SHARED"]
            )
        ),
    ]

    result = strip_shared_boilerplate(docs, threshold=0.9)

    assert "SHARED" not in result[0].page_content
    assert "\n\n\n" not in result[0].page_content
    assert result[0].page_content == "Intro A\n\nBody A"


def test_keeps_content_when_threshold_not_met():
    """Keep content when boilerplate does not meet the threshold."""
    docs = [
        _page("Home", ["Unique A"]),
        Document(page_content="Totally different page with no shared lines"),
    ]

    result = strip_shared_boilerplate(docs, threshold=0.9)

    # With only one of two docs containing the header, nothing is stripped.
    assert "121 Platform User Manual" in result[0].page_content


def test_single_document_is_unchanged():
    """Leave a single document unchanged."""
    docs = [_page("Home", ["Body"])]

    result = strip_shared_boilerplate(docs, threshold=0.9)

    assert "121 Platform User Manual" in result[0].page_content
