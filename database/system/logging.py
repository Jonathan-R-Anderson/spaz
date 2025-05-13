import logging
import os
from ...config import Config

def setup_logger(name=None):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(Config.LOG_FILE_PATH), exist_ok=True)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(Config.LOG_FILE_PATH)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
