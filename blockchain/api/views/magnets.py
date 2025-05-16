from flask import Blueprint, request, jsonify
from web3 import Web3
from eth_account import Account
import json
import os
from dotenv import load_dotenv
from system.logging import setup_logger
from config import Config

# Set up logger
logger = setup_logger("magnets_routes")

# Load environment
load_dotenv()
logger.debug("[ENV] .env loaded")

# Read env vars
rpc_url = os.getenv("RPC_URL")
private_key = os.getenv("PRIVATE_KEY")

if not rpc_url or not private_key:
    logger.error("[ENV] Missing RPC_URL or PRIVATE_KEY in environment")
    raise EnvironmentError("Missing RPC_URL or PRIVATE_KEY in environment")

# Initialize Web3 and Account
try:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    account = Account.from_key(private_key)
    logger.info(f"[INIT] Web3 connected: {w3.is_connected()} | Using account: {account.address}")
except Exception as e:
    logger.exception("[INIT] Failed to initialize Web3 or account")
    raise

magnets_routes = Blueprint("magnets_routes", __name__)
contract_cache = {}

# Load contract with caching
def get_contract(name):
    if name in contract_cache:
        logger.debug(f"[CONTRACT] Cache hit for contract '{name}'")
        return contract_cache[name]
    
    try:
        with open(f"/contracts/{name}.abi.json") as f:
            abi = json.load(f)
        with open(f"/contracts/{name}.address.txt") as f:
            address = f.read().strip()
        contract = w3.eth.contract(address=address, abi=abi)
        contract_cache[name] = contract
        logger.info(f"[CONTRACT] Loaded contract '{name}' at address {address}")
        return contract
    except Exception as e:
        logger.exception(f"[CONTRACT] Failed to load contract '{name}'")
        raise

# Submit magnet route
@magnets_routes.route("/submit_magnet", methods=["POST"])
def submit_magnet():
    try:
        data = request.json
        logger.debug(f"[/submit_magnet] Request data: {data}")

        contract = get_contract("SpazMagnetStore")
        nonce = w3.eth.get_transaction_count(account.address)
        logger.debug(f"[/submit_magnet] Nonce: {nonce}")

        txn = contract.functions.addMagnet(data["magnet_url"]).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 250000,
            "gasPrice": w3.to_wei("5", "gwei")
        })

        signed = account.sign_transaction(txn)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)

        logger.info(f"[/submit_magnet] Transaction submitted: {tx_hash.hex()}")
        return jsonify({"tx_hash": tx_hash.hex()}), 200

    except Exception as e:
        logger.exception("[/submit_magnet] Failed to submit magnet")
        return jsonify({"error": str(e)}), 500

# Get magnets route
@magnets_routes.route("/get_magnets/<eth_address>", methods=["GET"])
def get_magnets(eth_address):
    try:
        logger.info(f"[/get_magnets] Fetching magnets for: {eth_address}")
        contract = get_contract("SpazMagnetStore")
        magnets = contract.functions.getMagnets(eth_address).call()
        logger.debug(f"[/get_magnets] Found {len(magnets)} magnets")
        return jsonify({"magnets": magnets}), 200
    except Exception as e:
        logger.exception(f"[/get_magnets] Failed to get magnets for {eth_address}")
        return jsonify({"error": str(e)}), 500
