import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Implement the setup_logger function to initialize the logger and set up the necessary handlers
def setup_logger(name: str = __name__) -> logging.Logger:
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
