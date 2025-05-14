import os
import json
from system.logging import setup_logger

logger = setup_logger(__name__)


def _load_json_file(path):
    logger.info(f"[load_json_file] Attempting to load JSON from: {path}")
    
    if not os.path.exists(path):
        logger.warning(f"[load_json_file] File does not exist: {path}")
        return []

    try:
        with open(path, 'r') as f:
            data = json.load(f)
            logger.debug(f"[load_json_file] Successfully loaded data from {path}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"[load_json_file] JSON decode error in {path}: {e}")
        return []
    except Exception as e:
        logger.error(f"[load_json_file] Unexpected error loading {path}: {e}")
        return []


def _save_json_file(path, data):
    logger.info(f"[save_json_file] Saving JSON data to: {path}")
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
            logger.debug(f"[save_json_file] Data successfully written to {path}")
    except Exception as e:
        logger.error(f"[save_json_file] Failed to write data to {path}: {e}")
        raise


def _allowed_file(filename):
    logger.debug(f"[allowed_file] Checking if filename is allowed: {filename}")
    # Placeholder always returning True; logging added for future rule implementation
    return True
