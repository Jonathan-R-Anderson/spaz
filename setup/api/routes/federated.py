"""Routes for managing federations of systems."""

import os
import uuid
from flask import Blueprint, jsonify, request

from services.state import federations, systems
from utils.common import generate_id

# Similar to ``kerberos_bp``, expose ``federated_bp`` for registration in the
# application factory.
federated_bp = Blueprint("federated", __name__)


# ---------------------------
# 1. Join Existing Federation
# ---------------------------
@federated_bp.route('/federate/join', methods=['POST'])
def join_federation():
    data = request.json
    federation_id = data.get("federation_id")
    system_name = data.get("name")
    address = data.get("address")
    public_key = data.get("public_key")

    if federation_id not in federations:
        return jsonify({"error": "Federation not found"}), 404

    system_id = generate_id()
    systems[system_id] = {
        "name": system_name,
        "address": address,
        "public_key": public_key,
        "federation_id": federation_id
    }
    federations[federation_id]["members"].append(system_id)

    return jsonify({"message": "Joined federation", "system_id": system_id})

# ---------------------------
# 2. Deploy Standalone System
# ---------------------------
@federated_bp.route('/federate/standalone', methods=['POST'])
def create_standalone():
    data = request.json
    system_id = generate_id()
    systems[system_id] = {
        "name": data.get("name"),
        "address": data.get("address"),
        "public_key": data.get("public_key"),
        "federation_id": None
    }
    return jsonify({"message": "Standalone system deployed", "system_id": system_id})

# ---------------------------
# 3. Create New Federation
# ---------------------------
@federated_bp.route('/federate/create', methods=['POST'])
def create_federation():
    data = request.json
    federation_id = generate_id()
    creator_id = generate_id()

    federations[federation_id] = {
        "name": data.get("federation_name"),
        "creator": creator_id,
        "members": [creator_id]
    }

    systems[creator_id] = {
        "name": data.get("name"),
        "address": data.get("address"),
        "public_key": data.get("public_key"),
        "federation_id": federation_id
    }

    return jsonify({
        "message": "New federation created",
        "federation_id": federation_id,
        "creator_system_id": creator_id
    })

# ---------------------------
# View All Federations
# ---------------------------
@federated_bp.route('/federate/list', methods=['GET'])
def list_federations():
    return jsonify(federations)

# ---------------------------
# View All Systems
# ---------------------------
@federated_bp.route('/federate/systems', methods=['GET'])
def list_systems():
    return jsonify(systems)
