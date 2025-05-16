from flask import Flask
from api.routes import blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    return app
