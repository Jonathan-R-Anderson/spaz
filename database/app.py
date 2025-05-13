# app.py
from flask import Flask
from config import Config
from extensions import db, redis_client
import logging
from logging.config import dictConfig

# Centralized logging setup
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'wsgi': {
            'class': 'logging.FileHandler',
            'filename': Config.LOG_FILE_PATH,
            'formatter': 'default',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi', 'console']
    }
})


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Avoid circular imports by importing here
    from api.routes import blueprint
    app.register_blueprint(blueprint)

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
