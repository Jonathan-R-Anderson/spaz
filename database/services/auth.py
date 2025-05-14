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
        user = Users.query.filter_by(eth_address=eth_address).first()
        if user:
            user.rtmp_secret = secret
            user.ip_address = ip_address
        else:
            user = Users(eth_address, secret, ip_address)
            db.session.add(user)
        db.session.commit()
        logger.info(f"[store_secret] Successfully stored secret for {eth_address}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"[store_secret] Failed to store secret for {eth_address}: {e}")
        raise
