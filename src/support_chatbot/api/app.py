"""Application factory and FastAPI configuration."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from support_chatbot import __version__
from support_chatbot.adapters.conversation_engine import LangGraphConversationEngine
from support_chatbot.adapters.document_loader import KreuzbergDocumentLoader
from support_chatbot.adapters.vector_store import AzureVectorStoreProvider
from support_chatbot.api.errors import register_exception_handlers
from support_chatbot.api.log import setup_logging
from support_chatbot.api.middleware import RequestIdMiddleware, RequestLoggingMiddleware
from support_chatbot.api.routes import router
from support_chatbot.config.manuals import available_manual_ids
from support_chatbot.services.chat_service import ChatService
from support_chatbot.services.manual_ingestion_service import ManualIngestionService
from support_chatbot.settings import AppSettings

logger = logging.getLogger(__name__)

DESCRIPTION = """
Offers level-1 support for 510's products and services.

Built by [NLRC 510](https://www.510.global/).
"""


def create_app(
    *,
    settings: AppSettings | None = None,
    chat_service_factory=None,
    ingestion_service_factory=None,
) -> FastAPI:
    """Build and configure the FastAPI application."""
    app_settings = settings or AppSettings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        setup_logging()
        app.state.settings = app_settings

        provider = None
        if chat_service_factory is None or ingestion_service_factory is None:
            provider = AzureVectorStoreProvider(app_settings)
            logger.info(
                "Resolved vector store indexes for environment %r: %s",
                app_settings.environment,
                {
                    manual_id: provider.index_name(manual_id)
                    for manual_id in available_manual_ids()
                },
            )

        engine = None
        if chat_service_factory is None:
            if provider is None:
                raise RuntimeError(
                    "Vector store provider is required for default chat service"
                )
            engine = LangGraphConversationEngine(app_settings, provider)
            app.state.chat_service = ChatService(engine)
        else:
            app.state.chat_service = chat_service_factory(app_settings)

        if ingestion_service_factory is None:
            if provider is None:
                raise RuntimeError(
                    "Vector store provider is required for default ingestion service"
                )
            app.state.ingestion_service = ManualIngestionService(
                app_settings, provider, KreuzbergDocumentLoader()
            )
        else:
            app.state.ingestion_service = ingestion_service_factory(app_settings)

        yield

        if engine is not None:
            engine.flush()

    app = FastAPI(
        title="support-chatbot",
        description=DESCRIPTION,
        version=__version__,
        lifespan=lifespan,
        license_info={
            "name": "Apache-2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0",
        },
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(router)
    register_exception_handlers(app)
    return app
