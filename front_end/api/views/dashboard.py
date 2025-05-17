from flask import (
    jsonify, request, send_from_directory, url_for,
    render_template, current_app as app, redirect
)
from ..routes import blueprint
import logging, os
from werkzeug.utils import safe_join

# --- 🧱 Serve Vite-built "loading" app ---
@blueprint.route("/loading")
def loading_screen():
    """Serve loading page (Vite index.html)."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"), "index.html"
    )

@blueprint.route("/loading/<path:path>")
def loading_static(path):
    """Serve other Vite-built files (JS, CSS, images)."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"), path
    )

@blueprint.route("/assets/<path:filename>")
def vite_assets(filename):
    """Serve Vite-generated assets with absolute paths."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist", "assets"), filename
    )


# --- 🧭 Dashboard Route (Flask-rendered template) ---
@blueprint.route('/dashboard/<eth_address>', methods=['GET'])
def dashboard_view(eth_address):
    logging.debug(f"Rendering dashboard for {eth_address}")
    return render_template('dashboard.html', eth_address=eth_address)


# --- 👤 User Profile App (SPA-style fallback to profile/index.html) ---
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


# --- 🔁 Catch-all: redirect to loading with original path ---
@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')
def fallback_to_loading(path):
    """Redirect unmatched paths to the Vite loading app."""
    logging.debug(f"Redirecting to /loading for unknown path: /{path}")
    return redirect(f"/loading?target=/{path}")
