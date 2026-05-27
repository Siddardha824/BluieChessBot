# gui/utils/logger.py

import logging

# Ensure logging configuration is initialized
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(name)s: %(message)s"
)

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance with the specified name."""
    return logging.getLogger(name)
