import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask import Blueprint, request, jsonify
import json
import os
from ...system.logging import setup_logger
from config import Config

# Setup logger
logger = setup_logger("register_contracts_routes")

register_contracts_routes = Blueprint("register_contracts_routes", __name__)

@register_contracts_routes.route("/register_contracts", methods=["POST"])
def register_contracts():
    try:
        data = request.json
        logger.info(f"[/register_contracts] Incoming contract registration for {len(data)} contracts")

        for name, entry in data.items():
            abi_path = f"/contracts/{name}.abi.json"
            address_path = f"/contracts/{name}.address.txt"

            # Write ABI
            try:
                with open(abi_path, "w") as f:
                    json.dump(entry["abi"], f)
                logger.debug(f"[/register_contracts] ABI written to {abi_path}")
            except Exception as e:
                logger.error(f"[/register_contracts] Failed to write ABI for {name}: {e}")
                raise

            # Write address
            try:
                with open(address_path, "w") as f:
                    f.write(entry["address"])
                logger.debug(f"[/register_contracts] Address written to {address_path}")
            except Exception as e:
                logger.error(f"[/register_contracts] Failed to write address for {name}: {e}")
                raise

        logger.info("[/register_contracts] All contracts successfully registered")
        return jsonify({"status": "registered"}), 200

    except Exception as e:
        logger.exception("[/register_contracts] Error during contract registration")
        return jsonify({"error": str(e)}), 500
