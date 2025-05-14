import os
import json
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Environment variables
SPAZ_LIVESTREAM_ADDRESS = os.getenv("SPAZ_LIVESTREAM_ADDRESS", "0x0")
SPAZ_MODERATION_ADDRESS = os.getenv("SPAZ_MODERATION_ADDRESS", "0x0")
SPAZ_LIVESTREAM_ABI_PATH = os.getenv("SPAZ_LIVESTREAM_ABI_PATH", "./contracts/SpazLivestream.json")
SPAZ_MODERATION_ABI_PATH = os.getenv("SPAZ_MODERATION_ABI_PATH", "./contracts/SpazModeration.json")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/spaz_contracts.log")
HELP_PORT = int(os.getenv("HELP_PORT", 5005))

# Configure logging
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Spaz contract server initializing...")

# Load ABIs from disk
def load_abi(path):
    try:
        logging.debug(f"Attempting to load ABI from {path}")
        with open(path) as f:
            abi = json.load(f)
            logging.info(f"Successfully loaded ABI from {path}")
            return abi
    except Exception as e:
        logging.error(f"Error loading ABI from {path}: {e}")
        return []

@app.route("/spaz_livestream")
def get_spaz_livestream():
    logging.info("GET /spaz_livestream requested")
    return jsonify({
        "address": SPAZ_LIVESTREAM_ADDRESS,
        "abi": load_abi(SPAZ_LIVESTREAM_ABI_PATH)
    })

@app.route("/spaz_moderation")
def get_spaz_moderation():
    logging.info("GET /spaz_moderation requested")
    return jsonify({
        "address": SPAZ_MODERATION_ADDRESS,
        "abi": load_abi(SPAZ_MODERATION_ABI_PATH)
    })

# Run Flask server
if __name__ == "__main__":
    logging.info(f"Starting Flask server on port {HELP_PORT}")
    app.run(host="0.0.0.0", port=HELP_PORT)
