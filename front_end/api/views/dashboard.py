from flask import (
    jsonify, request, send_from_directory, url_for,
    render_template, current_app as app, redirect
)
from ..routes import blueprint
import logging, os
from werkzeug.utils import safe_join


# --- 🧱 Serve loading page from Vite (default /loading/index.html) ---
@blueprint.route("/loading")
def loading_screen():
    """Serve loading page (Vite index.html)."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"), "index.html"
    )

@blueprint.route("/loading/<path:path>")
def loading_static(path):
    """Serve Vite loader JS/CSS/static assets."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"), path
    )


# --- 🔁 Endpoint used by loading app to check if a Vite app is ready ---
@blueprint.route("/load_app/<app_name>")
def load_app_check(app_name):
    app_path = os.path.join(app.static_folder, "apps", app_name, "index.html")
    if os.path.exists(app_path):
        logging.debug(f"[LOADER] App '{app_name}' is ready.")
        return jsonify({"status": "ready", "path": f"/static/apps/{app_name}/index.html"})
    logging.warning(f"[LOADER] App '{app_name}' not found.")
    return jsonify({"status": "not_found"}), 404


# --- 📦 Serve any app in /static/apps/<app_name> ---
@blueprint.route("/static/apps/<app_name>/<path:filename>")
def serve_app_static_file(app_name, filename):
    """Serve app JS/CSS/assets from compiled folder."""
    return send_from_directory(
        os.path.join(app.static_folder, "apps", app_name), filename
    )

@blueprint.route("/static/apps/<app_name>/")
def serve_app_index(app_name):
    """Serve index.html for the Vite app (e.g. /static/apps/welcome/)."""
    return send_from_directory(
        os.path.join(app.static_folder, "apps", app_name), "index.html"
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


# --- 🔁 Catch-all: redirect to /loading with ?target=/original/path ---
@blueprint.route('/', defaults={'path': ''})
@blueprint.route('/<path:path>')
def fallback_to_loading(path):
    """Redirect unmatched paths to the Vite loading app."""
    logging.debug(f"Redirecting to /loading for unknown path: /{path}")
    return redirect(f"/loading?target=/{path}")
