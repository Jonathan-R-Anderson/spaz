import os
import json
from flask import Blueprint, request, jsonify
from web3 import Web3

update_site_routes = Blueprint("update_site", __name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")))
MAGNET_CONTRACT_ADDRESS = os.getenv("MAGNET_CONTRACT_ADDRESS", "0x000000000000000000000000000000000000dEaD")
MAGNET_CONTRACT_ABI_PATH = os.getenv("MAGNET_CONTRACT_ABI_PATH", "./abi/SpazLivestream.json")

with open(MAGNET_CONTRACT_ABI_PATH) as f:
    magnet_contract_abi = json.load(f)

magnet_contract = w3.eth.contract(
    address=Web3.to_checksum_address(MAGNET_CONTRACT_ADDRESS),
    abi=magnet_contract_abi
)

@update_site_routes.route("/commit_magnet", methods=["POST"])
def commit_magnet():
    data = request.get_json()
    eth_address = data.get("eth_address")
    magnet_url = data.get("magnet_url")
    file_path = data.get("file_path", "")

    if not all([eth_address, magnet_url]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        tx = magnet_contract.functions.updateThemeMagnet(magnet_url).build_transaction({
            'from': Web3.to_checksum_address(eth_address),
            'nonce': w3.eth.get_transaction_count(eth_address),
            'gas': 300000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })

        # Replace with actual signing logic if needed
        # signed_tx = w3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
        # tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return jsonify({"message": f"Magnet committed for {eth_address}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
