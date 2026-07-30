"""Fixtures for the slow, live-service integration smoke tests.

These fixtures build the real chat pipeline (Azure OpenAI + Azure AI Search) so
an end-to-end run can confirm the wiring against live services. They skip
cleanly when the environment is not configured, so the default unit run stays
fast and green without any cloud credentials. Answer-quality evaluation is
handled by Langfuse automated evals, not here.
"""

from __future__ import annotations

import pytest

from support_chatbot.settings import AppSettings


@pytest.fixture(scope="session")
def eval_settings() -> AppSettings:
    """Load real settings from the environment, skipping when unavailable."""
    try:
        settings = AppSettings()
    except Exception as exc:  # missing required env vars / no .env
        pytest.skip(f"Live settings unavailable, skipping integration tests: {exc}")
    return settings


@pytest.fixture(scope="session")
def provider(eval_settings: AppSettings):
    """Live Azure AI Search vector store provider."""
    from support_chatbot.adapters.vector_store import AzureVectorStoreProvider

    return AzureVectorStoreProvider(eval_settings)


@pytest.fixture(scope="session")
def chat_service(eval_settings: AppSettings, provider):
    """Live chat service backed by Azure OpenAI + Azure AI Search."""
    from support_chatbot.adapters.conversation_engine import LangGraphConversationEngine
    from support_chatbot.adapters.prompt_provider import LangfusePromptProvider
    from support_chatbot.services.chat_service import ChatService

    prompt_provider = LangfusePromptProvider(eval_settings)
    engine = LangGraphConversationEngine(eval_settings, provider, prompt_provider)
    return ChatService(engine, prompt_provider)
