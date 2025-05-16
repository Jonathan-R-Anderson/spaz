from flask import Blueprint, jsonify
import json

config_routes = Blueprint("config_routes", __name__)

CONFIG_PATH = "/app/config.json"

@config_routes.route("/load_config", methods=["GET"])
def load_config():
    with open(CONFIG_PATH, "r") as f:
        return jsonify(json.load(f))
