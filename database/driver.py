# app.py
import logging
from logging.config import dictConfig
from flask import Flask
from ...config import Config
from extensions import db, redis_client

# Centralized logging setup
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
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

logger = logging.getLogger(__name__)

def create_app(testing=False):
    logger.info("[create_app] Initializing Flask app...")
    app = Flask(__name__)
    
    logger.debug("[create_app] Loading config from Config object")
    app.config.from_object(Config)

    if testing:
        logger.warning("[create_app] App is running in TESTING mode — skipping some config overrides")

    # Initialize database
    try:
        db.init_app(app)
        logger.info("[create_app] Database initialized successfully")
    except Exception as e:
        logger.error(f"[create_app] Failed to initialize database: {e}")

    # Register blueprints
    try:
        from api.routes import blueprint
        app.register_blueprint(blueprint)
        logger.info("[create_app] API blueprint registered")
    except Exception as e:
        logger.error(f"[create_app] Failed to register API blueprint: {e}")

    return app


if __name__ == '__main__':
    logger.info("[main] Starting Flask app from __main__")
    app = create_app()

    with app.app_context():
        try:
            db.create_all()
            logger.info("[main] Database tables created successfully")
        except Exception as e:
            logger.error(f"[main] Failed to create database tables: {e}")

    try:
        logger.info("[main] Running app on http://0.0.0.0:5003")
        app.run(host='0.0.0.0', port=5003, debug=True)
    except Exception as e:
        logger.critical(f"[main] Unhandled exception during app.run: {e}")
        raise
