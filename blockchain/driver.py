import os
import time
import json
import requests
from flask import Flask
from dotenv import load_dotenv
from api.routes import blueprint
from system.logging import setup_logger
from config import Config

# Load environment variables
load_dotenv()

# Constants
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/spaz_contracts.log")
HELP_PORT = int(os.getenv("HELP_PORT", 5005))
required_contracts = ["SpazMagnetStore", "SpazLivestream", "SpazModeration"]

# Setup logger
logger = setup_logger("spaz_bootstrap")

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logger.info("[BOOT] Logger initialized")
logger.info(f"[BOOT] HELP_PORT set to {HELP_PORT}")

def wait_for_contracts():
    logger.info("⏳ Waiting for contract ABI/address files...")
    while True:
        missing = []
        for name in required_contracts:
            abi_path = f"/contracts/{name}.abi.json"
            address_path = f"/contracts/{name}.address.txt"
            if not os.path.exists(abi_path) or not os.path.exists(address_path):
                missing.append(name)
        if not missing:
            logger.info("✅ All required contract files are present.")
            break
        logger.debug(f"⏳ Still waiting for: {missing}")
        time.sleep(1)

def register_contracts_from_files():
    logger.info("[REGISTER] Preparing to load and register contracts...")
    contracts = {}
    try:
        for name in required_contracts:
            abi_path = f"/contracts/{name}.abi.json"
            address_path = f"/contracts/{name}.address.txt"

            with open(abi_path) as f:
                abi = json.load(f)
            with open(address_path) as f:
                address = f.read().strip()
            contracts[name] = {"abi": abi, "address": address}

            logger.debug(f"[REGISTER] Loaded {name}: {address}")

        res = requests.post(f"http://localhost:{HELP_PORT}/register_contracts", json=contracts)
        res.raise_for_status()
        logger.info("✅ Contracts registered successfully.")
    except Exception as e:
        logger.exception("❌ Failed to register contracts")

def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    logger.info("[FLASK] Blueprint registered")
    return app

if __name__ == "__main__":
    logger.info("[BOOT] Starting Spaz contract bootstrapper")
    wait_for_contracts()

    # Start Flask first so register_contracts can connect to it
    app = create_app()
    from threading import Thread
    logger.info(f"[FLASK] Launching Flask app on port {HELP_PORT}")
    Thread(target=lambda: app.run(host="0.0.0.0", port=HELP_PORT)).start()

    # Give Flask time to start up
    time.sleep(2)

    # Register contracts
    register_contracts_from_files()
