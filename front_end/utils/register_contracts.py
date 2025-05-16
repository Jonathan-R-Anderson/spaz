import sys
import os

# 🔧 Ensure /app is in the Python path so system and config modules are found
project_root = "/app"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import time
import json
import requests
from config import Config
from system.logging import setup_logger

logger = setup_logger("spaz_register")

HELP_PORT = int(os.getenv("HELP_PORT", 5005))


def wait_for_contracts():
    logger.info("⏳ Waiting for contract ABI/address files...")
    while True:
        missing = []
        for name in Config.REQUIRED_CONTRACTS:
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
        for name in Config.REQUIRED_CONTRACTS:
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


if __name__ == "__main__":
    wait_for_contracts()
    time.sleep(2)  # or better: replace with socket connection check
    register_contracts_from_files()
