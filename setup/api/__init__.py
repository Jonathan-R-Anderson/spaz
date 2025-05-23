from flask import Flask
from api.routes.kerberos import kerberos_bp
from api.routes.federated import federated_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(kerberos_bp)
    app.register_blueprint(federated_bp)
    return app
