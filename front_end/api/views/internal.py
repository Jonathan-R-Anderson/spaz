from flask import request, jsonify
from ..routes import blueprint
from config import Config
import requests, logging

@blueprint.route('/verify_secret', methods=['GET'])
def verify_secret():
    logging.info("[verify_secret] Received verification request")

    stream_key = request.args.get("name")  # whole string: 0xabc...&secret=xyz
    ip_address = request.remote_addr

    logging.info(f"[verify_secret] Incoming raw stream_key: {stream_key} from {ip_address}")

    if not stream_key or '&' not in stream_key:
        logging.warning("[verify_secret] Malformed stream key")
        return '', 403

    try:
        parts = dict(q.split('=') for q in stream_key.split('&'))
        eth_address = next(k for k in parts if k.startswith("0x"))
        secret = parts.get('secret')
    except Exception as e:
        logging.error(f"[verify_secret] Failed to parse stream key: {e}")
        return '', 403

    if not eth_address or not secret:
        logging.warning("[verify_secret] Missing eth_address or secret after parsing")
        return '', 403

    # Call internal verification
    verify_response = requests.post(
        f"{Config.DATABASE_URL}/verify_secret",
        json={"eth_address": eth_address, "secret": secret},
        timeout=10,
    )

    if verify_response.status_code == 200:
        logging.info(f"[verify_secret] ✅ Verified {eth_address}")
        return '', 204
    else:
        logging.warning(f"[verify_secret] ❌ Verification failed for {eth_address}")
        return '', 403

