from flask import Flask
from flask_restful import Api
from .routes import blueprint
import os
from ...config import Config

api = Api()

def create_app():
    app = Flask(__name__, static_url_path='')
    app.config.from_object(Config)
    app.config['TEMPLATES_AUTO_RELOAD'] = os.getenv('TEMPLATES_AUTO_RELOAD', True)
    app.register_blueprint(blueprint)
    app.url_map.strict_slashes = False
    api.init_app(app)
    return app
