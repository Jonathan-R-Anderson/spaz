import os
import json
from pathlib import Path
from flask import Blueprint, request, jsonify
from web3 import Web3
from system.logging import setup_logger
from config import Config

# Setup logger
logger = setup_logger("update_site_routes")

update_site_routes = Blueprint("update_site", __name__)

# Web3 setup
web3_provider = os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")
w3 = Web3(Web3.HTTPProvider(web3_provider))
logger.info(f"[INIT] Web3 provider set to: {web3_provider} | Connected: {w3.is_connected()}")

MAGNET_CONTRACT_ADDRESS = os.getenv("MAGNET_CONTRACT_ADDRESS", "0x000000000000000000000000000000000000dEaD")
# Resolve the ABI path relative to this file so tests can run from any CWD
default_abi_path = Path(__file__).resolve().parents[2] / "abi" / "SpazLivestream.json"
MAGNET_CONTRACT_ABI_PATH = os.getenv("MAGNET_CONTRACT_ABI_PATH", str(default_abi_path))

try:
    with open(MAGNET_CONTRACT_ABI_PATH) as f:
        magnet_contract_abi = json.load(f)
    logger.info(f"[INIT] Loaded ABI from {MAGNET_CONTRACT_ABI_PATH}")
except Exception as e:
    logger.exception(f"[INIT] Failed to load ABI: {e}")
    raise

try:
    magnet_contract = w3.eth.contract(
        address=Web3.to_checksum_address(MAGNET_CONTRACT_ADDRESS),
        abi=magnet_contract_abi
    )
    logger.info(f"[INIT] Contract initialized at {MAGNET_CONTRACT_ADDRESS}")
except Exception as e:
    logger.exception(f"[INIT] Failed to initialize contract: {e}")
    raise

@update_site_routes.route("/commit_magnet", methods=["POST"])
def commit_magnet():
    try:
        data = request.get_json()
        logger.info(f"[/commit_magnet] Incoming data: {data}")

        eth_address = data.get("eth_address")
        magnet_url = data.get("magnet_url")
        file_path = data.get("file_path", "")

        if not all([eth_address, magnet_url]):
            logger.warning("[/commit_magnet] Missing required fields")
            return jsonify({"error": "Missing required fields"}), 400

        eth_address = Web3.to_checksum_address(eth_address)
        nonce = w3.eth.get_transaction_count(eth_address)
        logger.debug(f"[/commit_magnet] Nonce for {eth_address}: {nonce}")

        tx = magnet_contract.functions.updateThemeMagnet(magnet_url).build_transaction({
            'from': eth_address,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })

        logger.info(f"[/commit_magnet] Transaction built for {eth_address} with magnet: {magnet_url}")
        logger.debug(f"[/commit_magnet] TX Object: {tx}")

        # Note: Signing and sending the transaction is currently commented out.
        # signed_tx = w3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
        # tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        # logger.info(f"[/commit_magnet] Transaction submitted: {tx_hash.hex()}")

        return jsonify({"message": f"Magnet committed for {eth_address}"}), 200

    except Exception as e:
        logger.exception("[/commit_magnet] Failed to commit magnet")
        return jsonify({"error": str(e)}), 500
