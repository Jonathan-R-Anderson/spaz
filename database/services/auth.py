import random
import hmac
import hashlib
import requests
import string
from models import Users
from extensions import db
from config import Config

from system.logging import setup_logger
logger = setup_logger(__name__)

HMAC_SECRET_KEY = Config.HMAC_SECRET_KEY


def _generate_secret():
    secret = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    logger.debug(f"[generate_secret] Generated secret: {secret}")
    return secret


def _hash_secret(secret):
    try:
        hashed = hmac.new(HMAC_SECRET_KEY.encode(), secret.encode(), hashlib.sha256).hexdigest()
        logger.debug(f"[hash_secret] Hashed secret for input '{secret}': {hashed}")
        return hashed
    except Exception as e:
        logger.error(f"[hash_secret] Error hashing secret: {e}")
        raise


def _store_secret(eth_address, secret, ip_address):
    logger.info(f"[store_secret] Storing secret for eth_address={eth_address}, ip_address={ip_address}")
    try:
        new_user = Users(eth_address=eth_address, rtmp_secret=secret, ip_address=ip_address)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"[store_secret] Successfully stored secret for {eth_address}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"[store_secret] Failed to store secret for {eth_address}: {e}")
        raise


def _fetch_secret_from_api(eth_address):
    logger.info(f"[fetch_secret_from_api] Fetching secret for eth_address={eth_address}")
    try:
        url = f"http://localhost:5003/get_secret/{eth_address}"
        logger.debug(f"[fetch_secret_from_api] Sending GET request to {url}")
        response = requests.get(url, timeout=5)
        logger.debug(f"[fetch_secret_from_api] Response status code: {response.status_code}")
        
        if response.status_code == 200:
            secret = response.json().get('secret')
            logger.info(f"[fetch_secret_from_api] Retrieved secret for {eth_address}")
            return secret
        else:
            logger.warning(f"[fetch_secret_from_api] Failed with status {response.status_code} for {eth_address}")
            return None
    except Exception as e:
        logger.error(f"[fetch_secret_from_api] Exception fetching secret for {eth_address}: {e}")
        return None
