import os
import time
import json
import logging
import requests
from flask import Flask
from dotenv import load_dotenv
from api.routes import blueprint

# Load environment variables
load_dotenv()

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/spaz_contracts.log")
HELP_PORT = int(os.getenv("HELP_PORT", 5005))

os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.DEBUG)

required_contracts = ["SpazMagnetStore", "SpazLivestream", "SpazModeration"]

def wait_for_contracts():
    print("⏳ Waiting for contract ABI/address files...")
    while True:
        if all(
            os.path.exists(f"/contracts/{name}.abi.json") and os.path.exists(f"/contracts/{name}.address.txt")
            for name in required_contracts
        ):
            break
        time.sleep(1)

def register_contracts_from_files():
    contracts = {}
    for name in required_contracts:
        with open(f"/contracts/{name}.abi.json") as f:
            abi = json.load(f)
        with open(f"/contracts/{name}.address.txt") as f:
            address = f.read().strip()
        contracts[name] = {"abi": abi, "address": address}

    try:
        res = requests.post("http://localhost:5005/register_contracts", json=contracts)
        res.raise_for_status()
        print("✅ Contracts registered successfully.")
    except Exception as e:
        print(f"❌ Failed to register contracts: {e}")

def create_app():
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    return app

if __name__ == "__main__":
    wait_for_contracts()

    # Start Flask first so register_contracts can connect to it
    app = create_app()
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=HELP_PORT)).start()

    # Give server a moment to boot
    time.sleep(2)

    # Register contracts
    register_contracts_from_files()
