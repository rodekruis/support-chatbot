"""Configuration for the manuals the chatbot can scrape and index.

A "manual" describes one documentation site: where to scrape it from
(``root_url`` / ``base_url`` / ``exclude_dirs``) and, optionally, how to chunk
it for indexing (``chunk_size`` / ``chunk_overlap``). When chunking is omitted,
documents are indexed without splitting. Definitions live in the
``manuals.yaml`` file next to this module so they ship with the package.
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources

import yaml

from support_chatbot.domain.models import ManualConfig

_MANUALS_RESOURCE = "manuals.yaml"
_DEFAULT_PROMPT_FILE = "prompts/support_chatbot_prompt.md"


@lru_cache(maxsize=1)
def _load_registry() -> dict[str, ManualConfig]:
    raw_text = (
        resources.files("support_chatbot.config")
        .joinpath(_MANUALS_RESOURCE)
        .read_text(encoding="utf-8")
    )
    data = yaml.safe_load(raw_text) or {}
    manuals = data.get("manuals", {})

    if not isinstance(manuals, dict):
        raise ValueError("Invalid manuals config: 'manuals' must be a mapping")

    registry: dict[str, ManualConfig] = {}
    for manual_id, item in manuals.items():
        if not isinstance(item, dict):
            raise ValueError(f"Invalid manual config for '{manual_id}': value must be a mapping")

        chunk_size = item.get("chunk_size")
        chunk_overlap = item.get("chunk_overlap")

        registry[manual_id] = ManualConfig(
            manual_id=manual_id,
            root_url=item["root_url"],
            base_url=item["base_url"],
            exclude_dirs=tuple(item.get("exclude_dirs", [])),
            chunk_size=int(chunk_size) if chunk_size is not None else None,
            chunk_overlap=int(chunk_overlap) if chunk_overlap is not None else None,
            prompt_file=item.get("prompt_file"),
            strip_boilerplate=bool(item.get("strip_boilerplate", True)),
            boilerplate_threshold=float(item.get("boilerplate_threshold", 0.9)),
        )

    if not registry:
        raise ValueError("Manual registry is empty")

    return registry


def available_manual_ids() -> list[str]:
    """Return the ids of all configured manuals."""
    return sorted(_load_registry())


def get_manual_config(manual_id: str) -> ManualConfig:
    """Return the configuration for a configured manual id."""
    registry = _load_registry()
    try:
        return registry[manual_id]
    except KeyError as exc:
        valid = ", ".join(sorted(registry))
        raise ValueError(f"Unknown manual_id: {manual_id!r}. Valid options: {valid}") from exc


def get_manual_prompt(manual_id: str) -> str:
    """Return the system prompt for a manual.

    Uses the manual's ``prompt_file`` if set, otherwise the packaged default
    prompt. Paths are resolved relative to the ``support_chatbot`` package so
    prompt files ship with the package.
    """
    prompt_file = get_manual_config(manual_id).prompt_file or _DEFAULT_PROMPT_FILE
    return resources.files("support_chatbot").joinpath(prompt_file).read_text(encoding="utf-8")
