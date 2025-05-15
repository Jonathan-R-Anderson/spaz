
import os
import logging
from config import Config

def ensure_static_dirs():
    for folder in [Config.STATIC_FOLDER, Config.HLS_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logging.info(f"Created directory: {folder}")
        else:
            logging.info(f"Directory already exists: {folder}")


def sanitize_eth_address(eth_address):
    return eth_address.split('&')[0] if '&' in eth_address else eth_address


