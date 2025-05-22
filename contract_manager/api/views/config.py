from flask import Blueprint, jsonify
import os
from dotenv import load_dotenv
from system.logging import setup_logger

# Initialize logger
logger = setup_logger("config_routes")

# Load environment variables
load_dotenv()
logger.debug("[config_routes] .env file loaded")

# Create Blueprint
config_routes = Blueprint("config_routes", __name__)

@config_routes.route("/load_config", methods=["GET"])
def load_config():
    logger.info("[/load_config] Endpoint called")

    rpc_url = os.getenv("RPC_URL")
    private_key = os.getenv("PRIVATE_KEY")

    if not rpc_url:
        logger.warning("[/load_config] RPC_URL is missing in environment")
    else:
        logger.debug(f"[/load_config] RPC_URL loaded: {rpc_url}")

    if not private_key:
        logger.warning("[/load_config] PRIVATE_KEY is missing in environment")
        private_key_masked = None
    else:
        private_key_masked = private_key[:6] + "..."
        logger.debug("[/load_config] PRIVATE_KEY loaded and masked")

    config = {
        "rpc_url": rpc_url,
        "private_key": private_key_masked
    }

    logger.info("[/load_config] Returning masked config JSON")
    return jsonify(config)
