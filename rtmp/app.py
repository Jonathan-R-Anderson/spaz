import os
import logging
import subprocess
import time
from multiprocessing import Process
from flask import Flask, request, jsonify
from threading import Lock
import requests
import hmac

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)

# Directories for static files and HLS files
STATIC_FOLDER = '/app/static'
HLS_FOLDER = os.path.join(STATIC_FOLDER, 'hls')
is_seeding_static = {}
snapshot_indices = {}
logging.info("Creating necessary directories if they don't exist.")

# Create directories if they don't exist
for folder in [STATIC_FOLDER, HLS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
        logging.info(f"Created directory: {folder}")
    else:
        logging.info(f"Directory already exists: {folder}")

app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['HLS_FOLDER'] = HLS_FOLDER

logging.info(f"Static folder: {STATIC_FOLDER}")
logging.info(f"HLS folder: {HLS_FOLDER}")

# Lock to avoid race conditions when accessing shared data
magnet_url_lock = Lock()

# Dictionary to track which eth_addresses are currently being monitored
is_monitoring_static = {}
is_monitoring_hls = {}
seeded_files = {}


def sanitize_eth_address(eth_address):
    return eth_address.split('&')[0] if '&' in eth_address else eth_address

def get_secret(eth_address):
    try:
        response = requests.get(f"http://profile_db:5003/get_secret/{eth_address}", timeout=5)
        if response.status_code == 200:
            return response.json().get("secret")
        else:
            logging.warning(f"[get_secret] Failed to get secret for {eth_address}: {response.status_code}")
    except Exception as e:
        logging.error(f"[get_secret] Exception while fetching secret: {e}")
    return None


# Function to store a magnet URL using the profile_db API
def store_magnet_url(eth_address, magnet_url, snapshot_index):
    logging.debug(f"Storing magnet URL for {eth_address}, snapshot {snapshot_index}")
    url = "http://psichos.is/store_magnet_url"
    payload = {
        "eth_address": eth_address,
        "magnet_url": magnet_url,
        "snapshot_index": snapshot_index
    }
    
    try:
        logging.info(f"Sending POST request to store magnet URL for {eth_address}, snapshot {snapshot_index}")
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info(f"Successfully stored magnet URL for {eth_address}, snapshot {snapshot_index}")
        else:
            logging.error(f"Failed to store magnet URL: {response.json()}")
    except Exception as e:
        logging.error(f"Error calling profile_db API to store magnet URL: {e}")

# Function to retrieve magnet URLs from profile_db
def retrieve_magnet_urls(eth_address):
    logging.debug(f"Retrieving magnet URLs for {eth_address}")
    url = f"http://profile_db:5003/get_magnet_urls/{eth_address}"
    
    try:
        logging.info(f"Sending GET request to retrieve magnet URLs for {eth_address}")
        response = requests.get(url)
        return response.json()
    except Exception as e:
        logging.error(f"Error calling profile_db API to retrieve magnet URLs: {e}")
        return None

# Function to stream and log output from the subprocess and store the magnet URL in the database
def stream_output(process, eth_address, snapshot_number):
    logging.debug(f"Started streaming output from subprocess for {eth_address}, snapshot {snapshot_number}")
    magnet_url = None
    
    while True:
        logging.debug("Reading output from subprocess")
        output = process.stdout.readline()  # Read line from stdout
        if output == '' and process.poll() is not None:
            logging.debug(f"No more output from subprocess for {eth_address}, snapshot {snapshot_number}, process may have finished.")
            break
        if output:
            logging.info(f"Subprocess output: {output.strip()}")
            if 'Magnet:' in output:
                magnet_url = output.split("Magnet: ")[1].strip()
                logging.info(f"Magnet URL found: {magnet_url}")
                
                # Store the magnet URL in the database by calling the profile_db API
                logging.info(f"Storing magnet URL {magnet_url} for {eth_address}, snapshot {snapshot_number}")
                store_magnet_url(eth_address, magnet_url, snapshot_number)
                break
    logging.debug(f"Magnet URL streaming complete for {eth_address}, snapshot {snapshot_number}: {magnet_url}")
    return magnet_url

    
@app.route('/magnet_urls/<eth_address>', methods=['GET'])
def magnet_url(eth_address):
    logging.info(f"Received request for magnet URLs for Ethereum address: {eth_address}")

    logging.info(f"Attempting to retrieve magnet URLs for {eth_address} from profile_db API.")
    magnet_urls = retrieve_magnet_urls(eth_address)
    logging.info(f"Response from profile_db for {eth_address}: {magnet_urls}")
    
    if magnet_urls.get("message") == "success":
        logging.info(f"Successfully retrieved magnet URLs for {eth_address}. Returning URLs.")
        return jsonify({"magnet_urls": magnet_urls.get("magnet_urls")}), 200
    else:
        logging.warning(f"Magnet URLs not found for {eth_address}. Attempting to start monitoring...")

        try:
            # Start static monitor
            logging.info(f"Calling /start_static_monitor for {eth_address}")
            static_resp = requests.post(
                "http://webtorrent_seeder:5002/start_static_monitor",
                json={"eth_address": eth_address},
                timeout=5
            )
            logging.info(f"/start_static_monitor response: {static_resp.status_code} {static_resp.text}")
        except Exception as e:
            logging.error(f"Failed to start static monitor: {e}")
            return jsonify({"error": "Failed to start static monitor"}), 500

        try:
            # Start HLS monitor
            logging.info(f"Calling /start_hls_monitor for {eth_address}")
            hls_resp = requests.post(
                "http://webtorrent_seeder:5002/start_hls_monitor",
                json={"eth_address": eth_address},
                timeout=5
            )
            logging.info(f"/start_hls_monitor response: {hls_resp.status_code} {hls_resp.text}")
        except Exception as e:
            logging.error(f"Failed to start HLS monitor: {e}")
            return jsonify({"error": "Failed to start HLS monitor"}), 500

        logging.info(f"Started monitoring for {eth_address}, but no magnet URLs available yet.")
        return jsonify({"error": "Magnet URL not found and monitoring started"}), 404

@app.route('/seed', methods=['POST'])
def seed_file():
    logging.info("Received request to seed a file.")

    eth_address = request.form.get('eth_address')
    snapshot_index = request.form.get('snapshot_index', 0)

    if not eth_address or not eth_address.startswith('0x') or len(eth_address) != 42:
        logging.error("Invalid or missing eth_address.")
        return jsonify({"error": "Valid eth_address is required"}), 400

    try:
        snapshot_index = int(snapshot_index)
    except ValueError:
        logging.error("Invalid snapshot_index, must be an integer.")
        return jsonify({"error": "snapshot_index must be an integer"}), 400

    if 'file' not in request.files:
        logging.error("File not provided in the request.")
        return jsonify({"error": "File is required"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected in the request.")
        return jsonify({"error": "No file selected"}), 400

    file_name = file.filename
    file_path = os.path.join(STATIC_FOLDER, file_name)

    if not os.path.exists(file_path):
        file.save(file_path)
        logging.info(f"Saved uploaded file to {file_path}")
    else:
        logging.info(f"File {file_path} already exists on disk.")

    if file_path in seeded_files:
        logging.info(f"File {file_name} is already seeded.")
        magnet_url = seeded_files[file_path]
        return jsonify({"magnet_url": magnet_url}), 200

    # Delegate seeding to webtorrent container via HTTP
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            data = {
                'eth_address': eth_address,
                'snapshot_index': snapshot_index
            }
            response = requests.post("http://webtorrent_seeder:5002/seed", files=files, data=data)

        if response.status_code == 200:
            magnet_url = response.json().get('magnet_url')
            logging.info(f"Magnet URL from webtorrent_seeder: {magnet_url}")
            seeded_files[file_path] = magnet_url
            return jsonify({"magnet_url": magnet_url}), 200
        else:
            logging.error(f"Seeding failed via webtorrent_seeder: {response.text}")
            return jsonify({"error": "Seeding failed"}), 500

    except Exception as e:
        logging.error(f"Exception contacting webtorrent_seeder: {e}")
        return jsonify({"error": "Failed to contact seeder"}), 500


def get_peer_count(magnet_url):
    try:
        response = requests.post("http://webtorrent_seeder:5002/peer_count", json={"magnet_url": magnet_url}, timeout=10)
        if response.status_code == 200:
            return response.json().get("peer_count", 0)
        else:
            logging.error(f"Error from peer_count endpoint: {response.text}")
    except Exception as e:
        logging.error(f"Exception while contacting webtorrent_seeder: {e}")
    return 0


def seed_all_static_files_for_user(eth_address):
    logging.info(f"[seed_all_static_files_for_user] Starting seeding process for {eth_address}")
    snapshot_indices.setdefault(eth_address, 0)

    while True:
        try:
            logging.debug(f"[{eth_address}] Listing files in HLS_FOLDER: {HLS_FOLDER}")
            for file_name in os.listdir(HLS_FOLDER):
                logging.debug(f"[{eth_address}] Inspecting file: {file_name}")

                if not file_name.startswith(eth_address):
                    logging.debug(f"[{eth_address}] Skipping file (wrong prefix): {file_name}")
                    continue
                if not file_name.endswith('.mp4'):
                    logging.debug(f"[{eth_address}] Skipping file (not mp4): {file_name}")
                    continue

                original_path = os.path.join(HLS_FOLDER, file_name)

                if not os.path.isfile(original_path):
                    logging.debug(f"[{eth_address}] Skipping (not a file): {original_path}")
                    continue
                if '.snapshot_' in file_name:
                    logging.debug(f"[{eth_address}] Skipping file (already snapshot): {file_name}")
                    continue

                # Assign and increment snapshot index
                snapshot_indices[eth_address] += 1
                index = snapshot_indices[eth_address]
                new_file_name = f"{eth_address}_snapshot_{index}.mp4"
                new_file_path = os.path.join(HLS_FOLDER, new_file_name)

                # Rename file if needed
                try:
                    logging.info(f"[{eth_address}] Renaming {original_path} -> {new_file_name}")
                    os.rename(original_path, new_file_path)
                except Exception as e:
                    logging.warning(f"[{eth_address}] Rename failed for {file_name}: {e}")
                    if not os.path.exists(new_file_path):
                        logging.debug(f"[{eth_address}] File not found after failed rename: {new_file_path}")
                        continue
                    logging.info(f"[{eth_address}] Using already renamed file: {new_file_path}")

                if new_file_path in seeded_files:
                    logging.debug(f"[{eth_address}] Already seeded: {new_file_path}")
                    continue

                # Begin seeding
                try:
                    logging.info(f"[{eth_address}] Starting seeding for: {new_file_path}")
                    with open(new_file_path, 'rb') as f:
                        files = {'file': (new_file_name, f)}
                        data = {'eth_address': eth_address, 'snapshot_index': index}
                        response = requests.post("http://webtorrent_seeder:5002/seed", files=files, data=data)

                    if response.status_code != 200:
                        logging.error(f"[{eth_address}] Seeding failed for {new_file_name}: {response.text}")
                        continue

                    magnet_url = response.json().get('magnet_url')
                    seeded_files[new_file_path] = magnet_url
                    logging.info(f"[{eth_address}] ✅ Seeded {new_file_name} with magnet: {magnet_url}")

                    # Monitor peer count in a loop
                    logging.debug(f"[{eth_address}] Monitoring peers for magnet: {magnet_url}")
                    while True:
                        peer_response = requests.post("http://webtorrent_seeder:5002/peer_count", json={"magnet_url": magnet_url})
                        if peer_response.status_code != 200:
                            logging.warning(f"[{eth_address}] Peer count check failed for {magnet_url}: {peer_response.text}")
                            break

                        peer_count = peer_response.json().get("peer_count", 0)
                        logging.info(f"[{eth_address}] Peer count for {magnet_url}: {peer_count}")

                        if peer_count > 10:
                            logging.info(f"[{eth_address}] Peer threshold reached. Stopping seeding for {magnet_url}")
                            requests.post("http://webtorrent_seeder:5002/stop_seeding", json={"eth_address": eth_address})
                            break

                        time.sleep(10)

                except Exception as e:
                    logging.error(f"[{eth_address}] ❌ Exception during seeding for {new_file_name}: {e}")

            logging.debug(f"[{eth_address}] Sleeping for 30 seconds before next pass...")
            time.sleep(30)

        except Exception as loop_error:
            logging.error(f"[seed_all_static_files_for_user] 🔥 Loop crashed for {eth_address}: {loop_error}")
            break


@app.route('/verify_secret', methods=['POST'])
def verify_secret():
    logging.info("[verify_secret] Received verification request")

    if request.is_json:
        logging.debug("[verify_secret] Request detected as JSON")
        eth_address = request.json.get('eth_address')
        secret = request.json.get('secret')
        ip_address = request.remote_addr
    else:
        logging.debug("[verify_secret] Request detected as form/url-encoded")
        stream_key = request.args.get('name') or request.form.get('name')
        logging.debug(f"[verify_secret] Raw stream_key: {stream_key}")

        if not stream_key or '&' not in stream_key:
            logging.warning("[verify_secret] Missing or malformed stream_key")
            return '', 403

        try:
            eth_address, secret = stream_key.split('&secret=')
            ip_address = request.remote_addr
            logging.debug(f"[verify_secret] Parsed eth_address: {eth_address}, secret: {secret}, ip: {ip_address}")
        except Exception as e:
            logging.error(f"[verify_secret] Error splitting stream_key: {e}")
            return '', 403

    if not eth_address or not secret:
        logging.warning(f"[verify_secret] Missing eth_address or secret. eth_address={eth_address}, secret={secret}")
        return '', 403

    # Store the streamer info before verifying
    try:
        logging.debug(f"[verify_secret] Attempting to store streamer info for {eth_address}")
        store_response = requests.post(
            "http://profile_db:5003/store_streamer_info",
            json={"eth_address": eth_address, "secret": secret, "ip_address": ip_address},
            timeout=5
        )
        if store_response.status_code != 200:
            logging.warning(f"[verify_secret] Failed to store streamer info: {store_response.text}")
            return '', 403
    except Exception as e:
        logging.error(f"[verify_secret] Exception during streamer info store: {e}")
        return '', 500

    # Now verify secret
    try:
        logging.debug(f"[verify_secret] Looking up stored secret for {eth_address}")
        secret_response = requests.get(f"http://profile_db:5003/get_secret/{eth_address}", timeout=5)
        if secret_response.status_code != 200:
            logging.warning(f"[verify_secret] No stored secret found for {eth_address}")
            return '', 403

        stored_secret = secret_response.json().get('secret')
    except Exception as e:
        logging.error(f"[verify_secret] Exception retrieving stored secret: {e}")
        return '', 500

    if hmac.compare_digest(secret, stored_secret):
        logging.info(f"[verify_secret] ✅ Secret verified for {eth_address}")
        return '', 204
    else:
        logging.warning(f"[verify_secret] ❌ Secret mismatch for {eth_address}")
        return '', 403


if __name__ == '__main__':
    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5004, debug=True)
