import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from custom_logging.stream_to_logger import StreamToLogger
from models.environment import get_log_file_path, get_log_folder_path
from models.environment import EXEC_MODE

logger = logging.getLogger("HunSpeechLogger")


def setup_logging():
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers
    while logger.handlers:
        logger.handlers.pop()

    log_folder = get_log_folder_path()
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    formatter = logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    # Create a file handler that overwrites the log file on startup
    file_handler = RotatingFileHandler(
        get_log_file_path(), maxBytes=5 * 1024 * 1024, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if EXEC_MODE != 'prod':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    sl = StreamToLogger(logger, logging.INFO)
    sys.stdout = sl
    sl = StreamToLogger(logger, logging.ERROR)
    sys.stderr = sl
