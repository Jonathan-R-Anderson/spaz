from flask import Blueprint, render_template
from shared import gremlinThreadABI, gremlinThreadAddress
from shared import gremlinAdminABI, gremlinAdminAddress
from shared import gremlinReplyABI, gremlinReplyAddress
from shared import allowed_file, FILE_DIR, save_whitelist
from shared import save_blacklist, blacklist, whitelist
from shared import app, gremlinProfileAddress, gremlinProfileABI
from shared import client, VPN_CONFIG_DIR, VPN_TEMPLATE_PATH
from shared import CERT_DIR, EASYRSA_DIR, WEBTORRENT_CONTAINER_URL
from shared import HMAC_SECRET_KEY, session_store, generate_ecc_key_pair
from shared import serialize_public_key
from shared import RTMP_URLS, DB_API_URL
from shared import gremlinChallengeABI, gremlinChallengeAddress
from shared import gremlinDAOABI, gremlinDAOAddress
from shared import gremlinAdminABI, gremlinAdminAddress
from shared import gremlinLeaderboardABI, gremlinLeaderboardAddress
from shared import gremlinJournalABI, gremlinJournalAddress
import json, os
from flask import request, jsonify, send_from_directory
import logging
from werkzeug.utils import secure_filename
import subprocess
from eth_account import Account
from eth_account.messages import encode_defunct
import requests
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
import base64
blueprint = Blueprint('blueprint', __name__)
# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("routes.log"),  # Specify log file
        logging.StreamHandler()  # Also log to console
    ]
)

# Replace this with your own message format or nonce generation
SECURE_MESSAGE = "Please sign this message to verify ownership of your Ethereum address."


@blueprint.route('/')
def index():
    return render_template('welcome.html')

@blueprint.route('/dashboard/<eth_address>', methods=['GET'])
def home(eth_address):
    return render_template('dashboard.html', eth_address=eth_address, 
                           gremlinProfileABI=json.dumps(gremlinProfileABI, ensure_ascii=False), 
                           gremlinProfileAddress=gremlinProfileAddress, 
                           gremlinLeaderboardAddress=gremlinLeaderboardAddress, 
                           gremlinLeaderboardABI=json.dumps(gremlinLeaderboardABI, ensure_ascii=False), 
                           gremlinJournalAddress=gremlinJournalAddress,
                           gremlinJournalABI=json.dumps(gremlinJournalABI, ensure_ascii=False))



@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle the image upload, send it to the torrent seeder container, and return the magnet link."""
    logging.info('Upload route accessed')  # Log route access
    
    if 'file' not in request.files:
        logging.error('No file part in the request')  # Log missing file part
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        logging.error('No file selected')  # Log empty filename
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Save the file to the shared volume mount (static directory)
        filename = secure_filename(file.filename)
        file_path = os.path.join(os.path.abspath("/app/static"), filename)  # Adjust to point to the shared volume
        
        logging.info(f"Attempting to save file: {filename} at {file_path}")  # Log file details

        try:
            # Save the file to the shared static directory
            file.save(file_path)
            logging.info(f"File successfully saved to {file_path}")

            # Send a request to the WebTorrent container to start seeding the file
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f)}
                logging.info(f"Sending file to WebTorrent container for seeding: {filename}")
                response = requests.post(f"{WEBTORRENT_CONTAINER_URL}/seed", files=files, timeout=30)

            # Check if the request was successful and get the magnet URL
            if response.status_code == 200:
                magnet_url = response.json().get('magnet_url')
                logging.info(f"Magnet URL received: {magnet_url}")
                return jsonify({"magnet_url": magnet_url}), 200
            else:
                logging.error(f"Failed to seed the file. WebTorrent container responded with: {response.text}")
                return jsonify({"error": response.text}), 500

        except Exception as e:
            logging.error(f"Error during file saving or torrent creation: {e}")
            return jsonify({"error": str(e)}), 500

    else:
        logging.error(f"Invalid file type: {file.filename}")
        return jsonify({"error": "Invalid file type"}), 400


#@app.route('/static/<path:filename>', methods=['GET'])
#def serve_static(filename):
#    """Serve the uploaded image."""
#    return send_from_directory(FILE_DIR, filename)

@app.route('/styles/<filename>', methods=['GET'])
def styles(filename):
    return send_from_directory(os.path.join('hosted', 'styles'), filename)

@app.route('/js/<filename>', methods=['GET'])
def js(filename):
    return send_from_directory(os.path.join('hosted', 'js'), filename)

# Route to add to blacklist
@app.route('/admin/blacklist/<item_type>', methods=['POST'])
def add_to_blacklist(item_type):
    data = request.json
    if item_type in ['tag', 'magnet', 'user']:
        blacklist_key = f"{item_type}s"  # "tags", "magnet_urls", or "users"
        item_value = data[item_type]
        if item_value not in blacklist[blacklist_key]:
            blacklist[blacklist_key].append(item_value)
            save_blacklist(blacklist)
            return jsonify({"message": f"{item_type.capitalize()} '{item_value}' added to blacklist"}), 200
        return jsonify({"error": f"{item_type.capitalize()} already blacklisted"}), 400
    return jsonify({"error": "Invalid blacklist type"}), 400

# Route to add to whitelist
@app.route('/admin/whitelist/<item_type>', methods=['POST'])
def add_to_whitelist(item_type):
    data = request.json
    if item_type in ['tag', 'magnet', 'user']:
        whitelist_key = f"{item_type}s"  # "tags", "magnet_urls", or "users"
        item_value = data[item_type]
        if item_value not in whitelist[whitelist_key]:
            whitelist[whitelist_key].append(item_value)
            save_whitelist(whitelist)
            return jsonify({"message": f"{item_type.capitalize()} '{item_value}' added to whitelist"}), 200
        return jsonify({"error": f"{item_type.capitalize()} already whitelisted"}), 400
    return jsonify({"error": "Invalid whitelist type"}), 400

# Route to get current blacklist
@app.route('/admin/blacklist', methods=['GET'])
def get_blacklist():
    return jsonify(blacklist)

# Route to get current whitelist
@app.route('/admin/whitelist', methods=['GET'])
def get_whitelist():
    return jsonify(whitelist)

@app.route('/users/<eth_address>', methods=['POST', 'GET'])
def user_profile(eth_address):
    if request.method == 'POST':
        # Get the current user's Ethereum address from the POST data
        current_user_eth_address = request.json.get('current_user_eth_address')

        # Convert both addresses to lowercase to ensure the comparison is case-insensitive
        is_owner = current_user_eth_address.lower() == eth_address.lower()

        # RTMP stream URL (only set if the user is the owner)
        rtmp_stream_url = None
        if is_owner:
            # Generate the RTMP stream URL specific to the owner (retrieve from mock DB)
            rtmp_stream_url = RTMP_URLS.get(eth_address, "")

        # Return JSON response with ownership and RTMP URL (if applicable)
        return jsonify({
            'is_owner': is_owner,
            'rtmp_stream_url': rtmp_stream_url if is_owner else '127.0.0.1'
        })

    # For GET requests, just render the template
    return render_template('profile.html', eth_address=eth_address, 
                           gremlinProfileABI=json.dumps(gremlinProfileABI, ensure_ascii=False), 
                           gremlinProfileAddress=gremlinProfileAddress, 
                           gremlinLeaderboardAddress=gremlinLeaderboardAddress, 
                           gremlinLeaderboardABI=json.dumps(gremlinLeaderboardABI, ensure_ascii=False), 
                           gremlinJournalAddress=gremlinJournalAddress,
                           gremlinJournalABI=json.dumps(gremlinJournalABI, ensure_ascii=False))

@app.route('/generate_rtmp_url', methods=['POST'])
def generate_rtmp_url():
    logging.info("Received request to generate RTMP URL.")

    # Extract the eth_address from the request
    eth_address = request.json.get('eth_address')
    logging.info(f"Extracted eth_address: {eth_address}")
    
    if not eth_address:
        logging.error("Ethereum address is required.")
        return jsonify({"error": "Ethereum address is required"}), 400
    
    # Call the API to generate and store a new secret for the eth_address
    logging.info(f"Calling API to generate secret for eth_address: {eth_address}")
    secret_response = requests.post(f"{DB_API_URL}/generate_secret", json={"eth_address": eth_address}, timeout=30)
    logging.info(f"Secret generation API responded with status code: {secret_response.status_code}")
    
    if secret_response.status_code != 200:
        logging.error("Failed to generate secret.")
        return jsonify({"error": "Failed to generate secret"}), 500
    
    # Parse the new secret from the response
    secret_data = secret_response.json()
    new_secret = secret_data.get('secret')
    logging.info(f"Retrieved new secret: {new_secret}")
    
    if not new_secret:
        logging.error("Failed to retrieve secret.")
        return jsonify({"error": "Failed to retrieve secret"}), 500
    
    # Create a new unique RTMP URL for the user with the secret embedded in it
    new_rtmp_url = f"rtmp://gremlin.codes:1935/live/{eth_address}?secret={new_secret}"
    logging.info(f"Generated new RTMP URL: {new_rtmp_url}")

    # Return the RTMP URL immediately so the stream can start
    logging.info(f"Successfully generated RTMP URL for eth_address: {eth_address}")
    return jsonify({'new_rtmp_url': new_rtmp_url}), 200

@app.route('/magnet_urls/<eth_address>', methods=['GET'])
def get_magnet_url(eth_address):
    """Fetch the magnet URLs for the given Ethereum address."""
    try:
        response = requests.get(f"{WEBTORRENT_CONTAINER_URL}/magnet_urls/{eth_address}", timeout=30)
        if response.status_code == 200:
            magnet_urls = response.json().get("magnet_urls")
            return jsonify({"magnet_urls": magnet_urls}), 200
        else:
            return jsonify({"error": "Failed to generate magnet URLs"}), 500
    except Exception as e:
        logging.error(f"Error communicating with WebTorrent container: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get-vpn-config/<eth_address>', methods=['POST'])
def get_vpn_config(eth_address):
    # Get the signed message and signature from the client request
    data = request.get_json()
    signed_message = data.get('signed_message')
    signature = data.get('signature')

    if not signed_message or not signature:
        return jsonify({"error": "Missing signed message or signature"}), 400

    # Verify the signed message
    try:
        message = encode_defunct(text=signed_message)
        recovered_address = Account.recover_message(message, signature=signature)

        # Ensure the recovered address matches the provided eth_address
        if recovered_address.lower() != eth_address.lower():
            return jsonify({"error": "Signature verification failed"}), 403

        # Path to the generated .ovpn config file
        vpn_config_path = f"/vpn-configs/{eth_address}.ovpn"
        
        if os.path.exists(vpn_config_path):
            return send_file(vpn_config_path, as_attachment=True)
        else:
            return jsonify({"error": "VPN configuration not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# List all containers (running and stopped)
@app.route('/containers', methods=['GET'])
def list_containers():
    containers = client.containers.list(all=True)
    container_list = [{'id': c.short_id, 'name': c.name, 'status': c.status} for c in containers]
    return jsonify(container_list)

# Start a new container from a given folder inside vuln_machines
@app.route('/start/<machine_name>', methods=['POST'])
def start_container(machine_name):
    try:
        # Build and run the container
        container = client.containers.run(
            f"vuln_machines/{machine_name}", 
            detach=True, 
            auto_remove=True,
            network_mode="none"  # No port exposure required, use Tor
        )
        return jsonify({'status': 'started', 'id': container.short_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Stop a running container by ID
@app.route('/stop/<container_id>', methods=['POST'])
def stop_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return jsonify({'status': 'stopped', 'id': container_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/generate-vpn-config/<eth_address>', methods=['POST'])
def generate_vpn_config(eth_address):
    """
    Generates or retrieves an OpenVPN configuration for the given Ethereum address.
    Ensures the same configuration is generated for the same address.
    """
    # Get the signed message and signature from the client request
    data = request.get_json()
    signed_message = data.get('signed_message')
    signature = data.get('signature')

    if not signed_message or not signature:
        return jsonify({"error": "Missing signed message or signature"}), 400

    # Verify the signed message
    try:
        message = encode_defunct(text=signed_message)
        recovered_address = Account.recover_message(message, signature=signature)

        # Ensure the recovered address matches the provided eth_address
        if recovered_address.lower() != eth_address.lower():
            return jsonify({"error": "Signature verification failed"}), 403

        # Generate the VPN configuration for the user
        vpn_config_dir = os.path.join(VPN_CONFIG_DIR, eth_address)
        vpn_config_path = os.path.join(vpn_config_dir, f"{eth_address}.ovpn")

        # Create the directory if it doesn't exist
        os.makedirs(vpn_config_dir, exist_ok=True)

        # Check if the configuration already exists, and return it if it does
        if os.path.exists(vpn_config_path):
            return send_file(vpn_config_path, as_attachment=True)

        # Generate the VPN config based on the template
        generate_openvpn_config(eth_address, vpn_config_path)

        if os.path.exists(vpn_config_path):
            return send_file(vpn_config_path, as_attachment=True)
        else:
            return jsonify({"error": "Failed to generate VPN configuration"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_openvpn_config(eth_address, output_path):
    """
    Generates the OpenVPN client configuration file for the given Ethereum address.
    """
    # Example of generating OpenVPN configuration using a template
    # You can customize this as needed to include additional options
    with open(VPN_TEMPLATE_PATH, 'r') as template_file:
        vpn_template = template_file.read()

    # Replace placeholders in the template with dynamic values (e.g., Ethereum address)
    vpn_config = vpn_template.replace("<ETH_ADDRESS>", eth_address)

    # Write the generated configuration to the output path
    with open(output_path, 'w') as config_file:
        config_file.write(vpn_config)

    # You can also add logic to generate client certificates and keys if needed
    # This part of the code would depend on your specific OpenVPN setup (e.g., EasyRSA)

@app.route('/generate-certificates', methods=['POST'])
def generate_certificates():
    eth_address = request.json.get("eth_address")
    
    if not eth_address:
        return jsonify({"error": "Ethereum address is required"}), 400

    # Setup EasyRSA for certificate generation
    if not os.path.exists(EASYRSA_DIR):
        os.makedirs(EASYRSA_DIR)
        subprocess.run(["easyrsa", "init-pki"], cwd=EASYRSA_DIR)
        subprocess.run(["easyrsa", "build-ca", "nopass"], cwd=EASYRSA_DIR, input=b"gremlin.codes\n")
        subprocess.run(["easyrsa", "gen-dh"], cwd=EASYRSA_DIR)
        subprocess.run(["easyrsa", "build-server-full", "server", "nopass"], cwd=EASYRSA_DIR)

    # Copy the necessary certificate files to the OpenVPN directory
    required_files = ['ca.crt', 'server.crt', 'server.key', 'dh.pem']
    for file in required_files:
        src = os.path.join(EASYRSA_DIR, f"pki/{file}")
        dest = os.path.join(CERT_DIR, file)
        if not os.path.exists(dest):
            subprocess.run(['cp', src, dest])

    # Generate the .ovpn file for the user
    ovpn_file_path = f"/app/static/openvpn/{eth_address}.ovpn"
    with open(ovpn_file_path, 'w') as ovpn_file:
        ovpn_file.write(f"""
client
dev tun
proto udp
remote YOUR_SERVER_IP 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
key-direction 1
<ca>
{open(CERT_DIR + '/ca.crt').read()}
</ca>
<cert>
{open(EASYRSA_DIR + f'/pki/issued/{eth_address}.crt').read()}
</cert>
<key>
{open(EASYRSA_DIR + f'/pki/private/{eth_address}.key').read()}
</key>
<tls-auth>
{open(EASYRSA_DIR + '/ta.key').read()}
</tls-auth>
    """)
    
    return jsonify({"message": "Certificates generated and configuration file created", "ovpn_file": ovpn_file_path})


@app.route('/start_session', methods=['POST'])
def start_session():
    eth_address = request.json.get('eth_address')

    if not eth_address:
        return jsonify({"error": "Ethereum address missing"}), 400

    # Generate ECC key pair
    private_key, public_key = generate_ecc_key_pair()

    # Store the private key securely (e.g., in a DB or session store)
    session_store[eth_address] = private_key

    # Serialize the public key to send it to the frontend
    public_key_serialized = serialize_public_key(public_key)

    return jsonify({
        "eth_address": eth_address,
        "public_key": public_key_serialized
    }), 200

@app.route('/verify', methods=['POST'])
def verify_hmac():
    eth_address = request.json.get('eth_address')
    encrypted_hmac = request.json.get('encrypted_hmac')

    if not eth_address or not encrypted_hmac:
        return jsonify({"error": "Missing Ethereum address or encrypted HMAC"}), 400

    # Retrieve the private key from the session store
    private_key = session_store.get(eth_address)

    if not private_key:
        return jsonify({"error": "Session expired or invalid"}), 400

    # Decrypt the encrypted HMAC using the private key
    try:
        encrypted_hmac_bytes = base64.b64decode(encrypted_hmac)
        hmac_secret = private_key.decrypt(
            encrypted_hmac_bytes,
            ec.ECIESHKDF(salt=None, algorithm=hashes.SHA256())
        )
        hmac_secret = hmac_secret.decode('utf-8')
    except Exception as e:
        return jsonify({"error": "Decryption failed"}), 500

    # Calculate the HMAC on the backend and verify it
    calculated_hmac = hmac.new(HMAC_SECRET_KEY.encode(), eth_address.encode(), hashlib.sha256).hexdigest()

    if hmac.compare_digest(calculated_hmac, hmac_secret):
        return jsonify({"message": "HMAC verified successfully"}), 200
    else:
        return jsonify({"error": "HMAC verification failed"}), 401

