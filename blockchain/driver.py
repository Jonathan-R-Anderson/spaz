import os
import json
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

# Load contract metadata from .env
SPAZ_LIVESTREAM_ADDRESS = os.getenv("SPAZ_LIVESTREAM_ADDRESS", "0x0")
SPAZ_MODERATION_ADDRESS = os.getenv("SPAZ_MODERATION_ADDRESS", "0x0")

SPAZ_LIVESTREAM_ABI_PATH = os.getenv("SPAZ_LIVESTREAM_ABI_PATH", "./contracts/SpazLivestream.json")
SPAZ_MODERATION_ABI_PATH = os.getenv("SPAZ_MODERATION_ABI_PATH", "./contracts/SpazModeration.json")

# Load ABIs from disk
def load_abi(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading ABI from {path}: {e}")
        return []

@app.route("/api/contracts/spaz_livestream")
def get_spaz_livestream():
    return jsonify({
        "address": SPAZ_LIVESTREAM_ADDRESS,
        "abi": load_abi(SPAZ_LIVESTREAM_ABI_PATH)
    })

@app.route("/api/contracts/spaz_moderation")
def get_spaz_moderation():
    return jsonify({
        "address": SPAZ_MODERATION_ADDRESS,
        "abi": load_abi(SPAZ_MODERATION_ABI_PATH)
    })

# Optional: Run this file as a standalone server
if __name__ == "__main__":
    port = int(os.getenv("HELP_PORT", 5001))
    app.run(host="0.0.0.0", port=port)
