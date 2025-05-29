import logging
import sys


def init_logger():
    logger = logging.getLogger("uvicorn.access")
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    for handler in logger.handlers:
        logger.removeHandler(handler)

    streamHandler = logging.StreamHandler(sys.stdout)

    handlers = [streamHandler]


    logging.basicConfig(
        format="%(asctime)s - [%(levelname)s]: %(message)s (%(pathname)s:%(lineno)d)",
        datefmt="%Y-%m-%d %H:%M:%S",
        level="DEBUG",
        handlers=handlers,
    )
