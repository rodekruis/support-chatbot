"""ASGI application entry point."""

from support_chatbot.api.app import create_app

app = create_app()
