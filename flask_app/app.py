import logging
import os
import threading
from shared import app, FILE_DIR
from blueprints.routes import blueprint
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

# Ensure logging is configured before any logging call
LOG_FILE_PATH = "app.log"

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),  # Specify log file
        logging.StreamHandler()  # Also log to console
    ]
)

# Flask logging
app.logger.addHandler(logging.FileHandler(LOG_FILE_PATH))
app.logger.addHandler(logging.StreamHandler())

# Flask application setup
CORS(app)
app.register_blueprint(blueprint)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Create directories if they don't exist
os.makedirs(FILE_DIR, exist_ok=True)