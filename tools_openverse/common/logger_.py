"""
This module provides a logger setup utility for the OpenVerse tools package.
It configures a logger with both file and console handlers, using a rotating file
handler for persistent logging and a stream handler for console output.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Set up and return a configured logger instance.

    The logger writes DEBUG and higher level logs to a rotating file in the 'logs'
    directory, and INFO and higher level logs to the console (stdout).

    Args:
        name (str): The name of the logger. Defaults to the module's __name__.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger__ = logging.getLogger(name)
    logger__.setLevel(logging.DEBUG)

    formater = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formater)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formater)

    logger__.addHandler(file_handler)
    logger__.addHandler(console_handler)

    return logger__
