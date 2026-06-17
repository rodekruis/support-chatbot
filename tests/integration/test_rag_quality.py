"""LLM-as-judge RAG quality checks for the chat service.

These tests run the real retrieval + generation pipeline and grade the answers
with a separate, stronger Azure OpenAI model (``MODEL_JUDGE``) to avoid the
self-preference bias of letting a model grade its own output. They are slow and
hit live Azure services, so they are marked ``integration`` and skip unless the
environment is configured (see ``tests/integration/conftest.py``).

Run explicitly with::

    uv run pytest -m integration
"""

from __future__ import annotations

import uuid

import pytest

from tests.integration.golden_questions import (
    available_manual_ids,
    get_golden_questions,
)
from support_chatbot.domain.models import AskRequest

pytestmark = pytest.mark.integration

FAITHFULNESS_THRESHOLD = 0.9
ANSWER_RELEVANCY_THRESHOLD = 0.9
RETRIEVAL_K = 5

# Cases are maintained in tests/integration/golden_questions.yaml and grouped
# by manual id so one registry can cover all manuals.
RAG_QUALITY_CASES = [
    (manual_id, question)
    for manual_id in available_manual_ids()
    for question in get_golden_questions(manual_id)
]


@pytest.mark.parametrize("manual_id,question", RAG_QUALITY_CASES)
def test_rag_answer_quality(manual_id, question, chat_service, provider, judge_model):
    """The bot's answer should be grounded in retrieved docs and on-topic."""
    from deepeval import assert_test
    from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
    from deepeval.test_case import LLMTestCase

    answer = chat_service.ask(
        AskRequest(
            question=question,
            thread_id=f"eval-{uuid.uuid4()}",
            manual_id=manual_id,
        )
    ).answer

    # Reconstruct the retrieval context the answer is grounded on.
    docs = provider.get_store(manual_id).similarity_search(question, k=RETRIEVAL_K)
    retrieval_context = [doc.page_content for doc in docs]

    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=retrieval_context,
    )

    assert_test(
        test_case,
        [
            FaithfulnessMetric(threshold=FAITHFULNESS_THRESHOLD, model=judge_model),
            AnswerRelevancyMetric(
                threshold=ANSWER_RELEVANCY_THRESHOLD, model=judge_model
            ),
        ],
    )
