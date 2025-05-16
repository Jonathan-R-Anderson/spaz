from flask import Blueprint, request, jsonify
import json
import os

register_contracts_routes = Blueprint("register_contracts_routes", __name__)

@register_contracts_routes.route("/register_contracts", methods=["POST"])
def register_contracts():
    data = request.json
    for name, entry in data.items():
        with open(f"/contracts/{name}.abi.json", "w") as f:
            json.dump(entry["abi"], f)
        with open(f"/contracts/{name}.address.txt", "w") as f:
            f.write(entry["address"])
    return jsonify({"status": "registered"}), 200

