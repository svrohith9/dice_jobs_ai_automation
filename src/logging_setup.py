from __future__ import annotations

import logging
import os
from pathlib import Path

from rich.logging import RichHandler

_CONFIGURED = False


def configure_logging(level: str | None = None, log_file: str = "application.log") -> None:
    """Configure root logger once, with Rich console output and a file handler.

    Safe to call multiple times — subsequent calls are no-ops.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    resolved = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric = getattr(logging, resolved, logging.INFO)

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=numeric,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(rich_tracebacks=True, show_path=False),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )
    _CONFIGURED = True
