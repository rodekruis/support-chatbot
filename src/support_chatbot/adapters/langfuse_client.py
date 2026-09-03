"""Shared Langfuse client construction.

The Langfuse SDK keeps one process-wide instance per public key. Constructing a
second client with the same key silently returns the first instance and drops
the new arguments, so the client must be built exactly once — in the
composition root — with its full configuration and then injected.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from support_chatbot.settings import AppSettings

if TYPE_CHECKING:
    from langfuse import Langfuse


def build_langfuse_client(settings: AppSettings) -> Langfuse | None:
    """Return a configured Langfuse client, or ``None`` when the keys are unset."""
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        return None
    from langfuse import Langfuse

    return Langfuse(
        public_key=settings.langfuse_public_key.get_secret_value(),
        secret_key=settings.langfuse_secret_key.get_secret_value(),
        base_url=settings.langfuse_base_url,
        environment=settings.environment,
    )
