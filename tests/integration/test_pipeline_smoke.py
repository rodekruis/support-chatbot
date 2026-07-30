"""Deterministic end-to-end smoke test for the live chat pipeline.

This does *not* judge answer quality (that lives in Langfuse automated evals on
production traffic). It only asserts the real retrieval + generation pipeline is
correctly wired against live Azure services: retrieval returns documents and
``ChatService.ask`` produces a non-empty answer for the requested manual.

It is marked ``integration`` and skips unless the environment is configured
(see ``tests/integration/conftest.py``), so the default unit run stays fast.

Run explicitly with::

    uv run -- python -m pytest -m integration
"""

from __future__ import annotations

import uuid

import pytest

from support_chatbot.config.manuals import available_manual_ids
from support_chatbot.domain.models import AskRequest

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def manual_id() -> str:
    """First configured manual id, used to exercise the live pipeline."""
    ids = available_manual_ids()
    if not ids:
        pytest.skip("No manuals configured; nothing to smoke-test")
    return ids[0]


def test_retrieval_returns_documents(provider, manual_id):
    """The live vector store should return documents for a configured manual."""
    docs = provider.get_store(manual_id).similarity_search("payment", k=3)

    assert docs, "expected the live vector store to return at least one document"
    assert all(doc.page_content.strip() for doc in docs)


def test_ask_returns_non_empty_answer(chat_service, manual_id):
    """The full pipeline should answer without erroring and echo the wiring."""
    response = chat_service.ask(
        AskRequest(
            question="How do I make a payment?",
            session_id=f"smoke-{uuid.uuid4()}",
            manual_id=manual_id,
        )
    )

    assert response.answer.strip(), "expected a non-empty answer from the pipeline"
