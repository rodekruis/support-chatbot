"""Golden RAG evaluation questions grouped by manual id for integration tests."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

_GOLDEN_QUESTIONS_FILE = Path(__file__).with_name("golden_questions.yaml")


@lru_cache(maxsize=1)
def _load_registry() -> dict[str, tuple[str, ...]]:
    data = yaml.safe_load(_GOLDEN_QUESTIONS_FILE.read_text(encoding="utf-8")) or {}
    manuals = data.get("manuals", {})

    if not isinstance(manuals, dict):
        raise ValueError("Invalid golden questions config: 'manuals' must be a mapping")

    registry: dict[str, tuple[str, ...]] = {}
    for manual_id, questions in manuals.items():
        if not isinstance(questions, list) or any(
            not isinstance(question, str) for question in questions
        ):
            raise ValueError(
                f"Invalid golden questions for '{manual_id}': value must be a list of strings"
            )
        if not questions:
            raise ValueError(
                f"Invalid golden questions for '{manual_id}': list cannot be empty"
            )
        registry[manual_id] = tuple(questions)

    if not registry:
        raise ValueError("Golden questions registry is empty")

    return registry


def get_golden_questions(manual_id: str) -> tuple[str, ...]:
    """Return all configured golden questions for a manual id."""
    registry = _load_registry()
    try:
        return registry[manual_id]
    except KeyError as exc:
        valid = ", ".join(sorted(registry))
        raise ValueError(
            f"Unknown manual_id for golden questions: {manual_id!r}. Valid options: {valid}"
        ) from exc


def available_manual_ids() -> tuple[str, ...]:
    """Return manual ids that have golden questions configured."""
    return tuple(sorted(_load_registry()))
