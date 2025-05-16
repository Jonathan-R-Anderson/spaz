import os
import json
import logging
from flask import Blueprint, jsonify

retrieve_contract_routes = Blueprint("contracts", __name__)

SPAZ_LIVESTREAM_ADDRESS = os.getenv("SPAZ_LIVESTREAM_ADDRESS", "0x0")
SPAZ_MODERATION_ADDRESS = os.getenv("SPAZ_MODERATION_ADDRESS", "0x0")
SPAZ_LIVESTREAM_ABI_PATH = os.getenv("SPAZ_LIVESTREAM_ABI_PATH", "./contracts/SpazLivestream.json")
SPAZ_MODERATION_ABI_PATH = os.getenv("SPAZ_MODERATION_ABI_PATH", "./contracts/SpazModeration.json")

def load_abi(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load ABI from {path}: {e}")
        return []

@retrieve_contract_routes.route("/spaz_livestream")
def get_spaz_livestream():
    return jsonify({
        "address": SPAZ_LIVESTREAM_ADDRESS,
        "abi": load_abi(SPAZ_LIVESTREAM_ABI_PATH)
    })

@retrieve_contract_routes.route("/spaz_moderation")
def get_spaz_moderation():
    return jsonify({
        "address": SPAZ_MODERATION_ADDRESS,
        "abi": load_abi(SPAZ_MODERATION_ABI_PATH)
    })
