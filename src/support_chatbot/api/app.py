from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from support_chatbot import __version__
from support_chatbot.adapters.vector_store import build_vector_store_bundle
from support_chatbot.api.errors import register_exception_handlers
from support_chatbot.api.middleware import RequestIdMiddleware, RequestLoggingMiddleware
from support_chatbot.api.routes import router
from support_chatbot.services.chat_service import ChatService
from support_chatbot.services.vector_store_service import VectorStoreService
from support_chatbot.settings import AppSettings

DESCRIPTION = """
Chat with [121 user manual](https://manual.121.global/) and get answers from support-chatbot.

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
    vector_store_service_factory=None,
) -> FastAPI:
    app_settings = settings or AppSettings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _setup_logging()
        app.state.settings = app_settings

        vector_bundle = None
        if chat_service_factory is None or vector_store_service_factory is None:
            vector_bundle = build_vector_store_bundle(app_settings)

        if chat_service_factory is None:
            if vector_bundle is None:
                raise RuntimeError(
                    "Vector store bundle is required for default chat service"
                )
            app.state.chat_service = ChatService(
                app_settings, vector_bundle.vector_store
            )
        else:
            app.state.chat_service = chat_service_factory(app_settings)

        if vector_store_service_factory is None:
            if vector_bundle is None:
                raise RuntimeError(
                    "Vector store bundle is required for default vector store service"
                )
            app.state.vector_store_service = VectorStoreService(
                app_settings,
                vector_bundle.vector_store,
                vector_bundle.index_client,
            )
        else:
            app.state.vector_store_service = vector_store_service_factory(app_settings)

        yield

    app = FastAPI(
        title="support-chatbot",
        description=DESCRIPTION,
        version=__version__,
        lifespan=lifespan,
        license_info={
            "name": "AGPL-3.0 license",
            "url": "https://www.gnu.org/licenses/agpl-3.0.en.html",
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
