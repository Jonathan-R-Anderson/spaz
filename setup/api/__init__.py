import os
from pathlib import Path
from flask import Flask, send_from_directory
from api.routes.kerberos import kerberos_bp
from api.routes.federated import federated_bp

def create_app():
    base_dir = Path(__file__).resolve().parent.parent
    dist_dir = base_dir / "web" / "dist"
    web_dir = base_dir / "web"
    static_dir = dist_dir if dist_dir.exists() else web_dir

    app = Flask(__name__, static_folder=str(static_dir), static_url_path="/")
    app.register_blueprint(kerberos_bp)
    app.register_blueprint(federated_bp)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path: str):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return app.send_static_file("index.html")

    return app
