import os
from flask import Flask
from config import Config 
from api.routes import blueprint
from flask_restful import Api

api = Api()

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static'),
        static_url_path='/static'
    )

    app.config.from_object(Config)
    app.config['TEMPLATES_AUTO_RELOAD'] = os.getenv('TEMPLATES_AUTO_RELOAD', True)

    app.register_blueprint(blueprint)
    app.url_map.strict_slashes = False
    api.init_app(app)

    return app
