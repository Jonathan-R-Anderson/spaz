from flask import Blueprint, request, jsonify
from web3 import Web3
from eth_account import Account
import json

magnets_routes = Blueprint("magnets_routes", __name__)

CONFIG_PATH = "/app/config.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

w3 = Web3(Web3.HTTPProvider(config["rpc_url"]))
account = Account.from_key(config["private_key"])
contract_cache = {}

def get_contract(name):
    if name not in contract_cache:
        with open(f"/contracts/{name}.abi.json") as f:
            abi = json.load(f)
        with open(f"/contracts/{name}.address.txt") as f:
            address = f.read().strip()
        contract_cache[name] = w3.eth.contract(address=address, abi=abi)
    return contract_cache[name]

@magnets_routes.route("/submit_magnet", methods=["POST"])
def submit_magnet():
    data = request.json
    contract = get_contract("SpazMagnetStore")
    txn = contract.functions.addMagnet(data["magnet_url"]).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 250000,
        "gasPrice": w3.to_wei("5", "gwei")
    })
    signed = account.sign_transaction(txn)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return jsonify({"tx_hash": tx_hash.hex()}), 200

@magnets_routes.route("/get_magnets/<eth_address>", methods=["GET"])
def get_magnets(eth_address):
    contract = get_contract("SpazMagnetStore")
    magnets = contract.functions.getMagnets(eth_address).call()
    return jsonify({"magnets": magnets})
