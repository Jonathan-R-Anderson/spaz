import base64
import logging
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from system.logging import setup_logger

logger = setup_logger(__name__)


def _generate_ecc_key_pair():
    logger.info("[generate_ecc_key_pair] Generating new ECC key pair using SECP256R1")
    try:
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        logger.debug(f"[generate_ecc_key_pair] Private key type: {type(private_key)}")
        logger.debug(f"[generate_ecc_key_pair] Public key type: {type(public_key)}")
        return private_key, public_key
    except Exception as e:
        logger.error(f"[generate_ecc_key_pair] Failed to generate ECC key pair: {e}")
        raise


def _serialize_public_key(public_key):
    logger.info("[serialize_public_key] Serializing public key to PEM format")
    try:
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        logger.debug(f"[serialize_public_key] PEM output (first 100 chars): {pem[:100]}...")
        return pem
    except Exception as e:
        logger.error(f"[serialize_public_key] Failed to serialize public key: {e}")
        raise


def _encrypt_secret(secret, public_key):
    logger.info("[encrypt_secret] Encoding secret using base64 (placeholder encryption)")
    try:
        encoded = base64.b64encode(secret.encode()).decode('utf-8')
        logger.debug(f"[encrypt_secret] Original secret: {secret}, Encoded: {encoded}")
        return encoded
    except Exception as e:
        logger.error(f"[encrypt_secret] Failed to encode secret: {e}")
        raise
