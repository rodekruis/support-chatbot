"""Unit tests for document loader title extraction."""

from support_chatbot.adapters.document_loader import _extract_title


def test_extract_title_prefers_h1():
    """Use the page-specific <h1> heading when present."""
    html = (
        "<html><head><title>Ignored - Site</title></head>"
        "<body><h1>Set up a project</h1></body></html>"
    )

    assert _extract_title(html) == "Set up a project"


def test_extract_title_strips_permalink_pilcrow():
    """Drop the trailing permalink pilcrow that themes add to headings."""
    html = "<h1>Manage users\u00b6</h1>"

    assert _extract_title(html) == "Manage users"


def test_extract_title_falls_back_to_title_without_suffix():
    """Fall back to <title>, removing a trailing site-name suffix."""
    html = (
        "<html><head><title>Dashboard - 121 Manual</title></head><body></body></html>"
    )

    assert _extract_title(html) == "Dashboard"


def test_extract_title_returns_none_when_absent():
    """Return None when neither an <h1> nor a <title> is available."""
    assert _extract_title("<html><body><p>No headings here.</p></body></html>") is None
