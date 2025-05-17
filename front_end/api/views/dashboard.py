from flask import jsonify, request, send_from_directory, url_for, render_template, current_app as app
from ..routes import blueprint
import logging, json, os
from utils.contracts import (
    get_spaz_livestream_abi, get_spaz_livestream_address,
    get_spaz_moderation_abi, get_spaz_moderation_address
)
from services.stream import RTMP_URLS
from werkzeug.utils import safe_join

@blueprint.route('/')
def index():
    logging.debug("Rendering welcome page.")
    return render_template('welcome.html')

@blueprint.route('/dashboard/<eth_address>', methods=['GET'])
def home(eth_address):
    logging.debug(f"Rendering dashboard for {eth_address}")
    return render_template('dashboard.html', eth_address=eth_address)

@blueprint.route('/users/<eth_address>', defaults={'path': ''})
@blueprint.route('/users/<eth_address>/<path:path>')
def user_profile(eth_address, path):
    profile_dir = os.path.join(app.static_folder, 'profile')
    
    target_path = safe_join(profile_dir, path)
    if not path or not os.path.exists(target_path):
        logging.debug(f"Serving profile index.html for {eth_address}")
        return send_from_directory(profile_dir, 'index.html')
    
    logging.debug(f"Serving static file: {target_path}")
    return send_from_directory(profile_dir, path)

@dynamic_bp.route('/', defaults={'path': ''})
@dynamic_bp.route('/<path:path>')
def forward_to_loading(path):
    return redirect(f"/loading?target=/{path}")