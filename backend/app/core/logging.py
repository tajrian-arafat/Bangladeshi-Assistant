"""Structured logging configuration."""

import logging
import sys
from typing import Literal

from app.core.config import get_settings


def setup_logging(level: str | None = None) -> None:
    """Configure root logger with a consistent format."""
    log_level = level or get_settings().log_level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(numeric_level)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if get_settings().database_echo else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
