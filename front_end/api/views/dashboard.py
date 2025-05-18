from flask import (
    jsonify, request, send_from_directory, url_for,
    render_template, current_app as app, redirect
)
from ..routes import blueprint
import logging, os
from werkzeug.utils import safe_join

# --- 🧱 Serve Vite "loading" app (index + static assets) ---
@blueprint.route("/loading")
def loading_screen():
    """Serve loading page (Vite index.html)."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"),
        "index.html"
    )

@blueprint.route("/loading/<path:path>")
def loading_static(path):
    """Serve other Vite-built files (JS, CSS, images)."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist"),
        path
    )

@blueprint.route("/assets/<path:filename>")
def vite_global_assets(filename):
    """Support assets Vite emits as absolute /assets/*.js/.css paths."""
    return send_from_directory(
        os.path.join(app.static_folder, "loading", "dist", "assets"),
        filename
    )


# --- 🔁 Loader: check if app exists in /static/apps/<app_name>/index.html ---
@blueprint.route("/load_app/<app_name>")
def load_app_check(app_name):
    """Used by the loader to verify if an app is available and pre-fetched."""
    app_path = os.path.join(app.static_folder, "apps", app_name, "index.html")
    if os.path.exists(app_path):
        logging.debug(f"[LOADER] App '{app_name}' is ready.")
        return jsonify({
            "status": "ready",
            "path": f"/static/apps/{app_name}/index.html"
        })
    logging.warning(f"[LOADER] App '{app_name}' not found.")
    return jsonify({"status": "not_found"}), 404


@blueprint.route("/static/apps/<app_name>/", defaults={"subpath": ""})
@blueprint.route("/static/apps/<app_name>/<path:subpath>")
def serve_vite_app(app_name, subpath):
    app_dir = os.path.join(app.static_folder, "apps", app_name)
    full_path = os.path.join(app_dir, subpath)

    # If actual file exists, serve it
    if subpath and os.path.exists(full_path):
        return send_from_directory(app_dir, subpath)

    # Otherwise serve index.html (for SPA routing like /users/0xabc)
    return send_from_directory(app_dir, "index.html")

# --- 🧭 Dashboard route (Jinja-rendered) ---
@blueprint.route("/dashboard/<eth_address>", methods=["GET"])
def dashboard_view(eth_address):
    logging.debug(f"Rendering dashboard for {eth_address}")
    return render_template("dashboard.html", eth_address=eth_address)

# --- 👤 Profile (SPA-style fallback to profile/index.html) ---
@blueprint.route("/users/<eth_address>", defaults={"path": ""})
@blueprint.route("/users/<eth_address>/<path:path>")
def user_profile(eth_address, path):
    profile_dir = os.path.join(app.static_folder, "profile")
    target_path = safe_join(profile_dir, path)

    if not path or not os.path.exists(target_path):
        logging.debug(f"Serving profile index.html for {eth_address}")
        return send_from_directory(profile_dir, "index.html")
    
    logging.debug(f"Serving profile file: {target_path}")
    return send_from_directory(profile_dir, path)

# --- 🔁 Catch-all: forward everything else to the loader ---
@blueprint.route("/", defaults={"path": ""})
@blueprint.route("/<path:path>")
def fallback_to_loading(path):
    """Fallback: redirect to /loading with original target in query."""
    logging.debug(f"Redirecting to /loading?url=/{path}")
    return redirect(f"/loading?url=/{path}")
