import os
from flask import Flask
from config import Config
from flask_restful import Api

from api.routes import blueprint
from api.routes.verify_proxy import verify_bp
from api.routes.dynamic_loader import dynamic_bp

api = Api()

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static'),
        static_url_path='/static'
    )
    app.register_blueprint(dynamic_bp)
    app.config.from_object(Config)
    app.config['TEMPLATES_AUTO_RELOAD'] = os.getenv('TEMPLATES_AUTO_RELOAD', True)

    # Register blueprints AFTER app is defined
    app.register_blueprint(blueprint)
    app.register_blueprint(verify_bp)

    app.url_map.strict_slashes = False
    api.init_app(app)

    return app
