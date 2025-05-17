from flask import (
    jsonify, request, send_from_directory, url_for,
    render_template, current_app as app, redirect
)
from ..routes import blueprint
import logging, os
from werkzeug.utils import safe_join

# --- 🔁 Catch-all fallback to loading screen ---
@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')
def forward_to_loading(path):
    return redirect(f"/loading?target=/{path}")


# --- 🧱 Serve Vite-built "loading" app ---
@blueprint.route("/loading")
def loading_screen():
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"), "index.html"
    )

@blueprint.route("/loading/<path:path>")
def loading_static(path):
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"), path
    )

# --- 🧱 Serve assets for /assets/... paths (used by Vite) ---
@blueprint.route("/assets/<path:filename>")
def vite_assets(filename):
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist", "assets"), filename
    )


# --- 🧭 Dashboard Route ---
@blueprint.route('/dashboard/<eth_address>', methods=['GET'])
def home(eth_address):
    logging.debug(f"Rendering dashboard for {eth_address}")
    return render_template('dashboard.html', eth_address=eth_address)


# --- 👤 User Profile App (SPA-style fallback) ---
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
