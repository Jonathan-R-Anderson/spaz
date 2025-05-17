from flask import jsonify, request, send_from_directory, url_for
from ..routes import blueprint
import logging, json
from utils.contracts import (
    get_spaz_livestream_abi, get_spaz_livestream_address,
    get_spaz_moderation_abi, get_spaz_moderation_address
)
from services.stream import RTMP_URLS
import os

@blueprint.route('/')
def index():
    logging.debug("Rendering welcome page.")
    return render_template('welcome.html')

@blueprint.route('/dashboard/<eth_address>', methods=['GET'])
def home(eth_address):
    logging.debug(f"Rendering dashboard for {eth_address}")
    return render_template('dashboard.html', eth_address=eth_address)

@blueprint.route('/users/<eth_address>', methods=['POST', 'GET'])
def user_profile(eth_address):
    if request.method == 'POST':
        current_user_eth_address = request.json.get('current_user_eth_address')
        is_owner = current_user_eth_address.lower() == eth_address.lower()
        rtmp_url = RTMP_URLS.get(eth_address, "psichos.is") if is_owner else "psichos.is"
        logging.debug(f"Profile POST for {eth_address}, owner={is_owner}")
        return jsonify({"is_owner": is_owner, "rtmp_stream_url": rtmp_url})

    # Serve the Vite-based static index.html from loading/
    logging.debug(f"Serving loading page for {eth_address}")
    return send_from_directory(os.path.join("static", "profile"), "index.html")
