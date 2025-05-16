from flask import Blueprint, request, jsonify
import requests

verify_bp = Blueprint("verify", __name__)

@verify_bp.route("/request-claim", methods=["POST"])
def request_claim():
    res = requests.post("http://localhost:4000/request-claim", json=request.json)
    return jsonify(res.json()), res.status_code

@verify_bp.route("/verify-claim", methods=["POST"])
def verify_claim():
    res = requests.post("http://localhost:4000/verify-claim", json=request.json)
    return jsonify(res.json()), res.status_code
