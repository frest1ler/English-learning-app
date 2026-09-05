"""Application logging with bounded files in the user state directory."""

import logging
from logging.handlers import RotatingFileHandler

from .paths import AppPaths


def configure_logging(paths: AppPaths, level: str = "INFO") -> logging.Logger:
    paths.ensure_writable()
    logger = logging.getLogger("english_learning")
    logger.setLevel(getattr(logging, level, logging.INFO))
    if not logger.handlers:
        handler = RotatingFileHandler(
            paths.log_dir / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        ))
        logger.addHandler(handler)
    return logger
