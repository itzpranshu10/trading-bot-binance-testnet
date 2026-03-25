"""Centralized logging configuration."""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Configure application logging once for console and file output."""

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    log_path = Path(__file__).resolve().parents[1] / "bot.log"
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger
