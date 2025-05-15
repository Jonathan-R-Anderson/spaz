import logging
import requests
from config import Config

def get_secret(eth_address):
    try:
        response = requests.get(f"{Config.DATABASE_URL}/get_secret/{eth_address}", timeout=5)
        if response.status_code == 200:
            return response.json().get("secret")
        else:
            logging.warning(f"[get_secret] Failed to get secret for {eth_address}: {response.status_code}")
    except Exception as e:
        logging.error(f"[get_secret] Exception while fetching secret: {e}")
    return None


def store_streamer_info(eth_address, secret, ip_address):
    try:
        response = requests.post(
            f"{Config.DATABASE_URL}/store_streamer_info",
            json={
                "eth_address": eth_address,
                "secret": secret,
                "ip_address": ip_address
            },
            timeout=5
        )
        return response
    except Exception as e:
        logging.error(f"[store_streamer_info] Exception while storing streamer info: {e}")
        return None
