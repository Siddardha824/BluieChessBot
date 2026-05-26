import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(name)s: %(message)s"
)


def get_logger(name):
    return logging.getLogger(name)