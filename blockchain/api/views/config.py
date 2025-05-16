from flask import Blueprint, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

config_routes = Blueprint("config_routes", __name__)

@config_routes.route("/load_config", methods=["GET"])
def load_config():
    config = {
        "rpc_url": os.getenv("RPC_URL"),
        "private_key": os.getenv("PRIVATE_KEY")[:6] + "..." if os.getenv("PRIVATE_KEY") else None  # mask for safety
    }
    return jsonify(config)
