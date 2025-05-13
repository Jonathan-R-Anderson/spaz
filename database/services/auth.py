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
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def _hash_secret(secret):
    return hmac.new(HMAC_SECRET_KEY.encode(), secret.encode(), hashlib.sha256).hexdigest()

def _store_secret(eth_address, secret, ip_address):
    new_user = Users(eth_address=eth_address, rtmp_secret=secret, ip_address=ip_address)
    db.session.add(new_user)
    db.session.commit()


def _fetch_secret_from_api(eth_address):
    try:
        response = requests.get(f"http://localhost:5003/get_secret/{eth_address}", timeout=5)
        if response.status_code == 200:
            return response.json().get('secret')
        else:
            logger.warning(f"[fetch_secret_from_api] Failed to get secret for {eth_address}: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"[fetch_secret_from_api] Exception fetching secret for {eth_address}: {e}")
        return None
