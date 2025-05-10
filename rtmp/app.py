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

# Function to convert a snapshot of HLS (.ts and .m3u8) files to a single .mp4 file using ffmpeg
def convert_hls_to_mp4(eth_address, snapshot_number):
    logging.info(f"Converting HLS snapshot {snapshot_number} to mp4 for {eth_address}")
    
    # Path to the m3u8 file for the eth_address
    m3u8_file = os.path.join(HLS_FOLDER, f"{eth_address}.m3u8")
    logging.debug(f"Looking for m3u8 file at {m3u8_file}")
    
    if not os.path.exists(m3u8_file):
        logging.error(f".m3u8 file not found for {eth_address}: {m3u8_file}")
        return None
    
    # Output mp4 file with an incrementing snapshot number
    output_mp4 = os.path.join(HLS_FOLDER, f"{eth_address}_snapshot_{snapshot_number}.mp4")
    logging.debug(f"Output MP4 will be saved to: {output_mp4}")
    
    # Use ffmpeg to convert the current snapshot of HLS (.ts) files and .m3u8 playlist to .mp4
    ffmpeg_cmd = [
        'ffmpeg', '-i', m3u8_file, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', '-t', '15', output_mp4
    ]
    
    logging.debug(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
    process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if process.returncode == 0:
        logging.info(f"Successfully converted HLS snapshot to mp4: {output_mp4}")
        return output_mp4
    else:
        logging.error(f"Error converting HLS to mp4: {process.stderr}")
        return None

# Function to monitor the HLS directory, convert .ts and .m3u8 to .mp4 in snapshots, and seed each snapshot
def monitor_hls_directory(eth_address):
    logging.info(f"Monitoring HLS directory for {eth_address}")
    snapshot_number = 0  # Start with snapshot 0

    while True:
        try:
            logging.debug(f"Checking for .ts files in the HLS folder for {eth_address}")
            ts_files = sorted(
                [f for f in os.listdir(HLS_FOLDER) if f.startswith(eth_address) and f.endswith('.ts')],
                key=lambda f: os.path.getmtime(os.path.join(HLS_FOLDER, f))
            )

            if not ts_files:
                logging.info(f"No .ts files found for {eth_address}, waiting for stream to start...")
                time.sleep(5)
                continue

            logging.info(f"Found {len(ts_files)} .ts files for {eth_address}. Preparing to create a new MP4 snapshot.")

            snapshot_number += 1
            logging.debug(f"Incremented snapshot number: {snapshot_number}")

            mp4_file = convert_hls_to_mp4(eth_address, snapshot_number)

            if mp4_file:
                logging.info(f"MP4 file {mp4_file} ready, starting to seed using webtorrent")

                process = subprocess.Popen(
                    ['/usr/bin/webtorrent', 'seed', mp4_file, '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                # Retrieve the magnet URL for the new snapshot, pass eth_address and snapshot_number
                magnet_url = stream_output(process, eth_address, snapshot_number)

                if magnet_url:
                    logging.info(f"Stored magnet URL for {eth_address} snapshot {snapshot_number}: {magnet_url}")
                else:
                    logging.error(f"Failed to generate magnet URL for {eth_address} snapshot {snapshot_number}")

            time.sleep(30)  # Take a new snapshot every 30 seconds

        except Exception as e:
            logging.error(f"Error monitoring HLS directory for {eth_address}: {e}")
            break

# Function to monitor the static directory for new files (excluding HLS) and update the magnet URL
def monitor_static_directory(eth_address):
    logging.info(f"Monitoring static directory for {eth_address}")
    latest_file = None

    while True:
        try:
            logging.debug(f"Checking for static files related to {eth_address} in {STATIC_FOLDER}")
            static_files = sorted([f for f in os.listdir(STATIC_FOLDER) if f.startswith(eth_address) and not f.endswith('.ts')],
                                  key=lambda f: os.path.getmtime(os.path.join(STATIC_FOLDER, f)))

            if static_files and static_files[-1] != latest_file:
                latest_file = static_files[-1]
                file_path = os.path.join(STATIC_FOLDER, latest_file)
                logging.info(f"Seeding static file for {eth_address}: {file_path}")

                process = subprocess.Popen(
                    ['/usr/bin/webtorrent', 'seed', file_path, '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                magnet_url = stream_output(process, eth_address, 0)

                if magnet_url:
                    logging.info(f"Stored magnet URL for static {eth_address}: {magnet_url}")

            time.sleep(5)
        except Exception as e:
            logging.error(f"Error monitoring static directory for {eth_address}: {e}")
            break

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
        logging.warning(f"Magnet URLs not found for {eth_address}. Initiating directory monitoring.")

        if not is_monitoring_static.get(eth_address, None):
            try:
                logging.info(f"Starting process to monitor static directory for {eth_address}.")
                static_process = Process(target=monitor_static_directory, args=(eth_address,))
                static_process.start()
                is_monitoring_static[eth_address] = True
                logging.info(f"Successfully started monitoring static directory for {eth_address}.")
            except Exception as e:
                logging.error(f"Error starting static directory monitoring for {eth_address}: {e}")
                return jsonify({"error": "Failed to monitor static directory"}), 500

        if not is_monitoring_hls.get(eth_address, None):
            try:
                logging.info(f"Starting process to monitor HLS directory for {eth_address}.")
                hls_process = Process(target=monitor_hls_directory, args=(eth_address,))
                hls_process.start()
                is_monitoring_hls[eth_address] = True
                logging.info(f"Successfully started monitoring HLS directory for {eth_address}.")
            except Exception as e:
                logging.error(f"Error starting HLS directory monitoring for {eth_address}: {e}")
                return jsonify({"error": "Failed to monitor HLS directory"}), 500

        logging.error(f"Magnet URL not found for {eth_address} and monitoring started.")
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

    # Save file if it doesn't already exist
    if not os.path.exists(file_path):
        file.save(file_path)
        logging.info(f"Saved uploaded file to {file_path}")
    else:
        logging.info(f"File {file_path} already exists on disk.")

    if file_path in seeded_files:
        logging.info(f"File {file_name} is already seeded.")
        magnet_url = seeded_files[file_path]
        return jsonify({"magnet_url": magnet_url}), 200

    logging.info(f"Seeding file {file_path}...")

    process = subprocess.Popen(
        ['/usr/bin/webtorrent', 'seed', file_path, '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    def seed_stream_output(process, file_path):
        magnet_url = None
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logging.info(f"Seeding output: {output.strip()}")
                if 'Magnet:' in output:
                    magnet_url = output.split("Magnet: ")[1].strip()
                    logging.info(f"Magnet URL found for {file_path}: {magnet_url}")
                    seeded_files[file_path] = magnet_url
                    return magnet_url
        return None

    magnet_url = seed_stream_output(process, file_path)

    if magnet_url:
        # Send POST request to store magnet URL in profile_db
        try:
            response = requests.post(
                "http://profile_db:5003/store_magnet_url",
                json={
                    "eth_address": eth_address,
                    "magnet_url": magnet_url,
                    "snapshot_index": snapshot_index
                }
            )
            if response.status_code == 200:
                logging.info("Successfully stored magnet URL via profile_db API.")
            else:
                logging.warning(f"Failed to store magnet URL: {response.json()}")
        except Exception as e:
            logging.error(f"Error while storing magnet URL: {e}")

        return jsonify({"magnet_url": magnet_url}), 200
    else:
        return jsonify({"error": "Failed to seed file and retrieve magnet URL"}), 500

@app.route('/verify_secret', methods=['POST'])
def verify_secret():
    logging.info("[verify_secret] Received verification request")
    logging.info(f"[verify_secret] {request.form}")

    stream_key = request.form.get("name")  # full key like "0xABC&secret=XYZ"

    ip_address = request.remote_addr
    if not stream_key or '&' not in stream_key:
        logging.warning("[verify_secret] Missing or malformed stream_key")
        return '', 403

    try:
        eth_address, secret = stream_key.split('&secret=')
        
    except Exception:
        logging.warning("[verify_secret] Failed to parse stream_key")
        return '', 403

    logging.info(f"[verify_secret] Parsed: eth_address={eth_address}, secret={secret}, ip_address={ip_address}")

    try:
        verify_response = requests.post(
            "http://profile_db:5003/verify_secret",
            json={"eth_address": eth_address, "secret": secret},
            timeout=10,
        )
        if verify_response.status_code == 204:
            logging.info(f"[verify_secret] ✅ Verified successfully for {eth_address}")
            if not is_seeding_static.get(eth_address):
                try:
                    logging.info(f"[verify_secret] Starting static seeding for {eth_address}")
                    static_process = Process(target=seed_all_static_files_for_user, args=(eth_address,))
                    static_process.start()
                    is_seeding_static[eth_address] = True
                except Exception as e:
                    logging.error(f"[verify_secret] Failed to start static seeding for {eth_address}: {e}")
            return '', 204
        else:
            logging.warning(f"[verify_secret] ❌ Verification failed for {eth_address}: {verify_response.text}")
            return '', 403
    except Exception as e:
        logging.error(f"[verify_secret] Exception occurred: {e}")
        return '', 500

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
    app.run(host='0.0.0.0', port=5004, debug=True)
