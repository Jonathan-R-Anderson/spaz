import os
import json
from flask import Blueprint, jsonify
from system.logging import setup_logger
from config import Config

# Initialize logger
logger = setup_logger("retrieve_contract_routes")

retrieve_contract_routes = Blueprint("contracts", __name__)

# Read environment variables
SPAZ_LIVESTREAM_ADDRESS = os.getenv("SPAZ_LIVESTREAM_ADDRESS", "0x0")
SPAZ_MODERATION_ADDRESS = os.getenv("SPAZ_MODERATION_ADDRESS", "0x0")
SPAZ_LIVESTREAM_ABI_PATH = os.getenv("SPAZ_LIVESTREAM_ABI_PATH", "./contracts/SpazLivestream.json")
SPAZ_MODERATION_ABI_PATH = os.getenv("SPAZ_MODERATION_ABI_PATH", "./contracts/SpazModeration.json")
SPAZ_MAGNET_STORE_ADDRESS = os.getenv("SPAZ_MAGNET_STORE_ADDRESS", "0x0")
SPAZ_MAGNET_STORE_ABI_PATH = os.getenv("SPAZ_MAGNET_STORE_ABI_PATH", "./contracts/SpazMagnetStore.json")

def load_abi(path):
    try:
        logger.debug(f"[load_abi] Attempting to load ABI from: {path}")
        with open(path) as f:
            abi = json.load(f)
        logger.info(f"[load_abi] Successfully loaded ABI from: {path}")
        return abi
    except Exception as e:
        logger.error(f"[load_abi] Failed to load ABI from {path}: {e}")
        return []

@retrieve_contract_routes.route("/spaz_livestream", methods=["GET"])
def get_spaz_livestream():
    logger.info("[/spaz_livestream] GET request received")
    response = {
        "address": SPAZ_LIVESTREAM_ADDRESS,
        "abi": load_abi(SPAZ_LIVESTREAM_ABI_PATH)
    }
    logger.debug(f"[/spaz_livestream] Returning contract data: address={SPAZ_LIVESTREAM_ADDRESS}")
    return jsonify(response), 200

@retrieve_contract_routes.route("/spaz_moderation", methods=["GET"])
def get_spaz_moderation():
    logger.info("[/spaz_moderation] GET request received")
    response = {
        "address": SPAZ_MODERATION_ADDRESS,
        "abi": load_abi(SPAZ_MODERATION_ABI_PATH)
    }
    logger.debug(f"[/spaz_moderation] Returning contract data: address={SPAZ_MODERATION_ADDRESS}")
    return jsonify(response), 200

@retrieve_contract_routes.route("/spaz_magnet_store", methods=["GET"])
def get_spaz_magnet_store():
    logger.info("[/spaz_magnet_store] GET request received")
    response = {
        "address": SPAZ_MAGNET_STORE_ADDRESS,
        "abi": load_abi(SPAZ_MAGNET_STORE_ABI_PATH)
    }
    logger.debug(f"[/spaz_magnet_store] Returning contract data: address={SPAZ_MAGNET_STORE_ADDRESS}")
    return jsonify(response), 200
