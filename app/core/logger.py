"""Logging configuration."""

import logging
import logging.handlers

from app.core.config import settings


def setup_logger(name: str) -> logging.Logger:
    """Set up logger with file and console handlers."""
    # Ensure logs directory exists
    settings.logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.handlers.RotatingFileHandler(
        settings.logs_dir / "app.log", maxBytes=10485760, backupCount=5  # 10MB
    )
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# Get logger for this module
logger = setup_logger(__name__)
