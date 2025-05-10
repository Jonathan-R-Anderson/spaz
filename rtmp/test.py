import os
import logging
import subprocess
import time
from multiprocessing import Process
from flask import Flask, request, jsonify
from threading import Lock
import requests

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

@app.route('/verify_secret', methods=['POST'])
def verify_secret():
    logging.info("[verify_secret] Received verification request")

    if request.is_json:
        logging.debug("[verify_secret] Request detected as JSON")
        eth_address = request.json.get('eth_address')
        secret = request.json.get('secret')
    else:
        logging.debug("[verify_secret] Request detected as form/url-encoded")
        stream_key = request.args.get('name') or request.form.get('name')
        logging.debug(f"[verify_secret] Raw stream_key: {stream_key}")

        if not stream_key or '&' not in stream_key:
            logging.warning("[verify_secret] Missing or malformed stream_key")
            return '', 403
        try:
            eth_address, secret = stream_key.split('&secret=')
            logging.debug(f"[verify_secret] Parsed eth_address: {eth_address}, secret: {secret}")
        except Exception as e:
            logging.error(f"[verify_secret] Error splitting stream_key: {e}")
            return '', 403

    if not eth_address or not secret:
        logging.warning(f"[verify_secret] Missing eth_address or secret. eth_address={eth_address}, secret={secret}")
        return '', 403

    logging.debug(f"[verify_secret] Looking up stored secret for {eth_address}")
    stored_secret = get_secret(eth_address)
    if not stored_secret:
        logging.warning(f"[verify_secret] No stored secret found for {eth_address}")
        return '', 403

    if hmac.compare_digest(secret, stored_secret):
        logging.info(f"[verify_secret] ✅ Secret verified for {eth_address}")
        return '', 204
    else:
        logging.warning(f"[verify_secret] ❌ Secret mismatch for {eth_address}")
        return '', 403

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


if __name__ == '__main__':
    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5091, debug=True)
