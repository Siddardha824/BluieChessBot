import logging
import os


DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL_ENV = "BLUIE_LOG_LEVEL"


def _configure_logging() -> None:
    log_level = os.getenv(LOG_LEVEL_ENV, DEFAULT_LOG_LEVEL).upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


_configure_logging()


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance with the specified name."""
    return logging.getLogger(name)
