"""support_chatbot package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("support-chatbot")
except PackageNotFoundError:
    __version__ = "0.0.1"
