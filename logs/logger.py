import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """Configure application-wide logging"""

    os.makedirs("logs", exist_ok=True)

    app.logger.setLevel(logging.INFO)

    # Clear Flask default handlers
    app.logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s (%(filename)s:%(lineno)d)"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=1_000_000,  # 1 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

    app.logger.info("Logger initialized successfully")
