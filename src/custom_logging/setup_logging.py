import sys
from custom_logging.stream_to_logger import StreamToLogger
import logging
from logging.handlers import RotatingFileHandler
from utils.general_utils import get_root_path

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

     # Remove any existing handlers
    while logger.handlers:
        logger.handlers.pop()

    # Create a file handler that overwrites the log file on startup
    file_handler = RotatingFileHandler(f'{get_root_path()}/log/output.log', maxBytes=5 * 1024 * 1024, mode='a')
    file_handler.setLevel(logging.DEBUG)

    # Optionally, add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Set a format for the log messages
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    sl = StreamToLogger(logger, logging.INFO)
    sys.stdout = sl
    sl = StreamToLogger(logger, logging.ERROR)
    sys.stderr = sl