import os
import logging
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from api import create_app
from config import Config
from gevent.pywsgi import WSGIServer

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

app = create_app()
CORS(app)