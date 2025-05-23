import uuid
import os
from flask import Blueprint, render_template, request



federations = {}
systems = {}

# ---------------------------
# Utilities
# ---------------------------
def generate_id():
    return str(uuid.uuid4())

# ---------------------------
# 1. Join Existing Federation
# ---------------------------
@app.route('/federate/join', methods=['POST'])
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
@app.route('/federate/standalone', methods=['POST'])
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
@app.route('/federate/create', methods=['POST'])
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
@app.route('/federate/list', methods=['GET'])
def list_federations():
    return jsonify(federations)

# ---------------------------
# View All Systems
# ---------------------------
@app.route('/federate/systems', methods=['GET'])
def list_systems():
    return jsonify(systems)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
