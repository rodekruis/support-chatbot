"""Application factory and FastAPI configuration."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from support_chatbot import __version__
from support_chatbot.adapters.document_loader import DoclingDocumentLoader
from support_chatbot.adapters.vector_store import AzureVectorStoreProvider
from support_chatbot.api.errors import register_exception_handlers
from support_chatbot.api.middleware import RequestIdMiddleware, RequestLoggingMiddleware
from support_chatbot.api.routes import router
from support_chatbot.services.chat_service import ChatService
from support_chatbot.services.manual_ingestion_service import ManualIngestionService
from support_chatbot.settings import AppSettings

DESCRIPTION = """
Offers level-1 support for products and services.

Built by [NLRC 510](https://www.510.global/).
"""


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
    for noisy_logger in ("urllib3", "azure", "requests_oauthlib"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


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
        _setup_logging()
        app.state.settings = app_settings

        provider = None
        if chat_service_factory is None or ingestion_service_factory is None:
            provider = AzureVectorStoreProvider(app_settings)

        if chat_service_factory is None:
            if provider is None:
                raise RuntimeError("Vector store provider is required for default chat service")
            app.state.chat_service = ChatService(app_settings, provider)
        else:
            app.state.chat_service = chat_service_factory(app_settings)

        if ingestion_service_factory is None:
            if provider is None:
                raise RuntimeError(
                    "Vector store provider is required for default ingestion service"
                )
            app.state.ingestion_service = ManualIngestionService(
                app_settings, provider, DoclingDocumentLoader()
            )
        else:
            app.state.ingestion_service = ingestion_service_factory(app_settings)

        yield

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
