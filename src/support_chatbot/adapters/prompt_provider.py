"""Langfuse-backed prompt provider adapter.

Loads system prompts from Langfuse prompt management instead of packaged files,
so prompt text can be edited and versioned in Langfuse and picked up without a
redeploy. Two kinds of prompts are used:

- ``citations``: product-agnostic, always used to add inline citations.
- ``<product>``: product-specific (named after the manual/product id, e.g.
  ``121``), used as the system prompt for that product's answers.

Which version is fetched is controlled by a Langfuse label derived from the
deployment environment (``prod`` maps to ``Production``; other environments use
their own name, e.g. ``dev``).
"""

from __future__ import annotations

from support_chatbot.domain.errors import ExternalServiceError
from support_chatbot.domain.ports import PromptProvider
from support_chatbot.settings import AppSettings

_CITATION_PROMPT_NAME = "citations"


class LangfusePromptProvider(PromptProvider):
    """Fetch system prompts from Langfuse prompt management."""

    def __init__(self, settings: AppSettings) -> None:
        """Create a Langfuse client, requiring the Langfuse credentials."""
        if not (settings.langfuse_public_key and settings.langfuse_secret_key):
            raise ExternalServiceError(
                "Langfuse credentials are required to load prompts; set "
                "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY."
            )
        from langfuse import Langfuse

        self._client = Langfuse(
            public_key=settings.langfuse_public_key.get_secret_value(),
            secret_key=settings.langfuse_secret_key.get_secret_value(),
            host=settings.langfuse_host,
        )
        self._label = self._label_for_environment(settings.environment)

    @staticmethod
    def _label_for_environment(environment: str) -> str:
        """Map the deployment environment to a Langfuse prompt label."""
        return "Production" if environment == "prod" else environment

    def get_product_prompt(self, product: str) -> str:
        """Return the product-specific system prompt named after ``product``."""
        return self._fetch(product)

    def get_citation_prompt(self) -> str:
        """Return the product-agnostic citation prompt."""
        return self._fetch(_CITATION_PROMPT_NAME)

    def _fetch(self, name: str) -> str:
        try:
            prompt = self._client.get_prompt(name, label=self._label, type="text")
        except Exception as exc:  # Langfuse has no stable public error hierarchy
            raise ExternalServiceError(
                f"Failed to load prompt {name!r} (label {self._label!r}) "
                f"from Langfuse: {exc}"
            ) from exc
        return prompt.prompt
