import os
import logging
from flask import Flask
from dotenv import load_dotenv
from api.routes import blueprint

# Load environment variables
load_dotenv()

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/spaz_contracts.log")
HELP_PORT = int(os.getenv("HELP_PORT", 5005))

os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    return app

if __name__ == "__main__":
    logging.info(f"Starting Flask server on port {HELP_PORT}")
    create_app().run(host="0.0.0.0", port=HELP_PORT)
