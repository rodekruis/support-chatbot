"""Centralized logging configuration."""

from __future__ import annotations

import logging
import sys

_NOISY_LOGGERS = ("urllib3", "azure", "requests_oauthlib")


def setup_logging() -> None:
    """Configure root logging for the whole application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )
    for noisy_logger in _NOISY_LOGGERS:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
