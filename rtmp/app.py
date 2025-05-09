from flask import Flask, request, jsonify
import requests
import logging
import os


app = Flask(__name__)

# Database API URL
DB_API_URL = "http://psichos.is:5003"
HLS_FOLDER = '/app/static/hls'

# Configure logging to output to the console
logging.basicConfig(level=logging.INFO)

# Generate a new secret for a given Ethereum address
@app.route('/generate_secret', methods=['POST'])
def generate_secret():
    eth_address = request.json.get('eth_address')
    ip_address = request.json.get('ip_address')

    if not eth_address:
        return jsonify({"error": "Ethereum address is required"}), 400

    if not ip_address:
        return jsonify({"error": "IP address is required"}), 400

    payload = {"eth_address": eth_address, "ip_address": ip_address}
    logging.info(f"Forwarding to DB_API_URL: {payload}")  # 🔍

    response = requests.post(f"{DB_API_URL}/generate_secret", json=payload)

    logging.info(f"DB_API_URL responded with {response.status_code}: {response.text}")  # 🔍

    return jsonify(response.json()), response.status_code


# Verify the secret provided by the RTMP server before starting the stream
@app.route('/verify_secret', methods=['POST'])
def verify_secret():
    eth_address = request.form.get("name")  # Ethereum address from the RTMP stream
    secret = request.form.get("secret")  # Secret provided by the client
    ip_address = request.remote_addr  # Capture the requester's IP address

    # Log the input parameters
    logging.info(f"Received request: eth_address={eth_address}, secret={secret}, ip_address={ip_address}")

    # Store the IP address in the database alongside the eth_address
    # Modify the database call to store the IP address
    response = requests.post(f"{DB_API_URL}/store_streamer_info", json={
        "eth_address": eth_address,
        "hashed_secret": secret,
        "ip_address": ip_address
    })

    # Log the response status code and content
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response content: {response.json()}")

    if response.status_code == 200:
        logging.info(f"Secret verified successfully and IP {ip_address} stored for eth_address: {eth_address}")
        return '', 204  # Return a 204 (No Content) if successful
    else:
        logging.error(f"Failed to verify secret or store IP for eth_address: {eth_address}")
        return '', 403  # Return a 403 (Forbidden) if the process fails

# Get the RTMP URL for an Ethereum address
@app.route('/get_rtmp_url/<eth_address>', methods=['GET'])
def get_rtmp_url(eth_address):
    response = requests.get(f"{DB_API_URL}/get_rtmp_url/{eth_address}")
    return jsonify(response.json()), response.status_code

@app.route('/on_publish_done', methods=['POST', 'GET'])
def on_publish_done():
    current_ip = request.remote_addr  # Capture the IP address of the requester
    
    # Retrieve the stored IP address for the eth_address from the database
    response = requests.get(f"{DB_API_URL}/get_streamer_eth_address/{current_ip}")
    stored_ip = response.json().get('ip_address')
    eth_address = response.json().get("eth_address")

    # Validate that the IP address matches the stored IP
    if current_ip == stored_ip:
        logging.info(f"IP address match for {eth_address}. Shutting down stream.")

        # Call the clear_magnet_urls endpoint to remove the magnet URLs
        clear_response = requests.delete(f"{DB_API_URL}/clear_magnet_urls/{eth_address}")
        if clear_response.status_code == 200:
            logging.info(f"Magnet URLs for {eth_address} cleared successfully.")
            
            # Clear all files related to the Ethereum address from the shared HLS directory
            try:
                clear_eth_address_files(eth_address)
                logging.info(f"All files related to {eth_address} have been deleted from {HLS_FOLDER}")
            except Exception as e:
                logging.error(f"Failed to delete files for {eth_address}: {e}")
        else:
            logging.error(f"Failed to clear magnet URLs for {eth_address}. Status: {clear_response.status_code}")

        return jsonify({"status": f"Stream for {eth_address} has ended"}), 200
    else:
        logging.error(f"IP address mismatch for {eth_address}. Unauthorized shutdown attempt.")
        return jsonify({"error": "Unauthorized shutdown attempt"}), 403


def clear_eth_address_files(eth_address):
    """
    Deletes all files related to the Ethereum address in the HLS directory.
    """
    for root, dirs, files in os.walk(HLS_FOLDER):
        for file in files:
            if file.startswith(eth_address):
                file_path = os.path.join(root, file)
                logging.info(f"Deleting file: {file_path}")
                os.remove(file_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, ssl_context=('/certs/fullchain.pem', '/certs/privkey.pem'))
