# driver.py
import logging
from logging.config import dictConfig
from flask import Flask
from config import Config
from extensions import db, redis_client
from api.routes import blueprint
from models.user import Users
from models.magnet import MagnetURL
from models.torrent import TorrentGroup, TorrentFile
import sys

# Logging setup
dictConfig({
    'version': 1,
    'formatters': {
        'default': {'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'},
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
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi', 'console'],
    }
})

logger = logging.getLogger(__name__)


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    if testing:
        app.config['TESTING'] = True

    db.init_app(app)
    app.register_blueprint(blueprint)
    return app


# Main execution path
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        if '--init-db' in sys.argv:
            logger.info("Initializing database tables...")
            db.create_all()
            logger.info("✅ Tables created.")
            sys.exit(0)

        logger.info("[driver] Starting Flask app on http://0.0.0.0:5003")
        for rule in app.url_map.iter_rules():
            logger.info(f"{rule.endpoint}: {rule.rule} [{','.join(rule.methods)}]")
        app.run(host='0.0.0.0', port=5003, debug=True)
