import os
import time
import json
import requests
from flask import Flask
from dotenv import load_dotenv

# Use the specific route you want
from api.views.register_contracts import register_contracts_routes
from system.logging import setup_logger
from config import Config

# Load environment variables
load_dotenv()

# Constants
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/spaz_contracts.log")
HELP_PORT = int(os.getenv("HELP_PORT", 5005))

# Setup logger
logger = setup_logger("spaz_bootstrap")

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logger.info("[BOOT] Logger initialized")
logger.info(f"[BOOT] HELP_PORT set to {HELP_PORT}")

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(register_contracts_routes)
    logger.info("[FLASK] register_contracts_routes blueprint registered")
    app.run(host="0.0.0.0", port=HELP_PORT)
