from flask import request, jsonify
from ..routes import blueprint
from config import Config
import requests, logging

@blueprint.route('/get_rtmp_url/<eth_address>', methods=['GET'])
def get_rtmp_url(eth_address):

    logging.info(f"[proxy_get_rtmp_url] Incoming request for eth_address: {eth_address}")

    try:
        # Construct full URL to DB container's endpoint
        db_url = f"{Config.DATABASE_URL}/get_rtmp_url/{eth_address}"
        logging.info(f"[proxy_get_rtmp_url] Forwarding to DB URL: {db_url}")

        # Send GET request to DB container
        response = requests.get(db_url, timeout=10)

        # Log and forward response
        logging.info(f"[proxy_get_rtmp_url] DB response status: {response.status_code}")
        logging.debug(f"[proxy_get_rtmp_url] DB response content: {response.text}")

        return (response.text, response.status_code, {'Content-Type': 'application/json'})

    except requests.exceptions.RequestException as e:
        logging.error(f"[proxy_get_rtmp_url] Error while contacting DB: {str(e)}")
        return jsonify({"error": "Failed to contact DB"}), 500
    





@blueprint.route('/generate_rtmp_url', methods=['POST'])
def generate_rtmp_url():
    logging.info("Generating RTMP URL")
    eth_address = request.json.get('eth_address')
    ip_address = request.json.get('ip_address')
    if not eth_address:
        logging.warning("Missing Ethereum address")
        return jsonify({"error": "Ethereum address is required"}), 400
    try:
        response = requests.post(f"{Config.DATABASE_URL}/generate_secret", json={"eth_address": eth_address, "ip_address": ip_address}, timeout=30)
        logging.debug(f"Secret generation response: {response.status_code} - {response.text}")
        if response.status_code != 200:
            return jsonify({"error": "Failed to generate secret"}), 500
        new_secret = response.json().get('secret')
        rtmp_url = f"rtmp://psichos.is:1935/live/{eth_address}?secret={new_secret}"
        return jsonify({"new_rtmp_url": rtmp_url}), 200
    except Exception as e:
        logging.exception("Error generating RTMP URL")
        return jsonify({"error": str(e)}), 500

