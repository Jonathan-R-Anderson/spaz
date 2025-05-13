from flask import jsonify
from ..routes import blueprint
from ...config import Config
import requests, logging

@blueprint.route('/magnet_urls/<eth_address>')
def get_magnet_url(eth_address):
    logging.info(f"Fetching magnet URLs for {eth_address}")
    try:
        response = requests.get(f"{Config.WEBTORRENT_CONTAINER_URL}/magnet_urls/{eth_address}", timeout=30, verify=False)
        if response.status_code == 200:
            return jsonify({"magnet_urls": response.json().get("magnet_urls")}), 200
        return jsonify({"error": "Failed to generate magnet URLs"}), 500
    except Exception as e:
        logging.exception("WebTorrent communication error")
        return jsonify({"error": str(e)}), 500
