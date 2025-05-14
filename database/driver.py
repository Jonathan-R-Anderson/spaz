# app.py
import logging
from logging.config import dictConfig
from flask import Flask
from config import Config
from extensions import db, redis_client
from api.routes import blueprint 

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
    app = Flask(__name__)
    app.config.from_object(Config)

    if testing:
        app.config["TESTING"] = True

    db.init_app(app)

    app.register_blueprint(blueprint)

    return app


if __name__ == '__main__':
    logger.info("[main] Starting Flask app from __main__")
    app = create_app()


    logger.info("[ROUTES] Listing all registered routes:")
    for rule in app.url_map.iter_rules():
        logger.info(f"{rule.endpoint}: {rule.rule} [{','.join(rule.methods)}]")


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
