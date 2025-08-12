import os
from flask import Flask, send_from_directory
from api.routes.kerberos import kerberos_bp
from api.routes.federated import federated_bp

def create_app():
    app = Flask(__name__, static_folder="web/dist", static_url_path="/")
    app.register_blueprint(kerberos_bp)
    app.register_blueprint(federated_bp)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path: str):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return app.send_static_file("index.html")

    return app
