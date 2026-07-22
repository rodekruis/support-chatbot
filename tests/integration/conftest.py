"""Fixtures for slow, live-service integration tests.

These fixtures build the real chat pipeline (Azure OpenAI + Azure AI Search) and
a separate judge model for LLM-as-judge evaluation. Everything skips cleanly
when the environment is not configured, so the default unit run stays fast and
green without any cloud credentials.
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
    if not settings.model_judge:
        pytest.skip("MODEL_JUDGE is not configured; skipping LLM-as-judge evals")
    return settings


@pytest.fixture(scope="session")
def judge_model(eval_settings: AppSettings):
    """A separate (ideally stronger) Azure OpenAI model used only to grade answers.

    Using a different deployment than ``MODEL_CHAT`` avoids the self-preference
    bias of letting the generating model score its own output.
    """
    models = pytest.importorskip("deepeval.models")
    return models.AzureOpenAIModel(
        model=eval_settings.model_judge,
        deployment_name=eval_settings.model_judge,
        api_key=eval_settings.azure_openai_api_key.get_secret_value(),
        api_version=eval_settings.azure_openai_api_version,
        base_url=eval_settings.azure_openai_endpoint,
        temperature=0,
    )


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
