import os
import logging
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from api import create_app
from ...config import Config

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
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Ensure upload directory exists
os.makedirs(Config.FILE_DIR, exist_ok=True)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        ssl_context=('/certs/fullchain.pem', '/certs/privkey.pem')
    )
