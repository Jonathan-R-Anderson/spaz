from flask import Flask
from flask_restful import Api
from .routes import blueprint

def create_app():
    app = Flask(__name__, static_url_path='')
    app.config.from_object('config.Config')
    app.register_blueprint(blueprint)
    api = Api(app)
    return app