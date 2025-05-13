from flask import request, jsonify
from ..routes import blueprint
from ...utils.crypto import _generate_ecc_key_pair, _serialize_public_key
from ...config import Config
from ...services.auth import session_store
import base64
import hmac
import hashlib
import logging

# Needed for the ECC decryption line
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


@blueprint.route('/start_session', methods=['POST'])
def start_session():
    eth_address = request.json.get('eth_address')
    logging.debug(f"Starting session for {eth_address}")
    if not eth_address:
        return jsonify({"error": "Ethereum address missing"}), 400
    private_key, public_key = _generate_ecc_key_pair()
    session_store[eth_address] = private_key
    return jsonify({"eth_address": eth_address, "public_key": _serialize_public_key(public_key)}), 200



@blueprint.route('/verify', methods=['POST'])
def verify_hmac():
    eth_address = request.json.get('eth_address')
    encrypted_hmac = request.json.get('encrypted_hmac')
    logging.debug(f"Verifying HMAC for {eth_address}")
    if not eth_address or not encrypted_hmac:
        return jsonify({"error": "Missing Ethereum address or encrypted HMAC"}), 400
    private_key = session_store.get(eth_address)
    if not private_key:
        return jsonify({"error": "Session expired or invalid"}), 400
    try:
        encrypted_hmac_bytes = base64.b64decode(encrypted_hmac)
        hmac_secret = private_key.decrypt(encrypted_hmac_bytes, ec.ECIESHKDF(salt=None, algorithm=hashes.SHA256()))
        hmac_secret = hmac_secret.decode('utf-8')
    except Exception as e:
        logging.exception("Decryption failed")
        return jsonify({"error": "Decryption failed"}), 500
    calculated_hmac = hmac.new(Config.HMAC_SECRET_KEY.encode(), eth_address.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(calculated_hmac, hmac_secret):
        return jsonify({"message": "HMAC verified successfully"}), 200
    return jsonify({"error": "HMAC verification failed"}), 401


