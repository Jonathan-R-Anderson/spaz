import os
import logging
import subprocess
import time
from multiprocessing import Process
from flask import Flask, request, jsonify
from threading import Lock
import requests
from threading import Thread

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
seed_processes = {}
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
    url = "http://profile_db:5003/store_magnet_url"
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

def stream_output(process, eth_address, snapshot_number):
    logging.debug(f"[stream_output] Started for {eth_address}, snapshot {snapshot_number}")
    magnet_url = None

    while True:
        output = process.stdout.readline()
        if output == '':
            output = process.stderr.readline()
        if output == '' and process.poll() is not None:
            logging.debug(f"[stream_output] No more output; process ended for {eth_address}")
            break
        if output:
            logging.info(f"[stream_output] Raw line: {output.strip()}")
            if 'Magnet:' in output:
                magnet_url = output.split("Magnet: ")[1].strip()
                logging.info(f"[stream_output] Found magnet URL: {magnet_url}")
                store_magnet_url(eth_address, magnet_url, snapshot_number)
                break

    logging.debug(f"[stream_output] Completed for {eth_address}: {magnet_url}")
    return magnet_url


def monitor_static_directory(eth_address):
    if is_monitoring_static.get(eth_address):
        logging.info(f"[monitor_static_directory] Already monitoring for {eth_address}")
        return
    is_monitoring_static[eth_address] = True
    logging.info(f"[monitor_static_directory] Starting monitor for {eth_address}")

    latest_file = None

    while True:
        try:
            logging.debug(f"[monitor_static_directory] Scanning static folder for {eth_address}")
            static_files = sorted(
                [f for f in os.listdir(STATIC_FOLDER)
                 if f.startswith(eth_address) and f.endswith('.mp4')],
                key=lambda f: os.path.getmtime(os.path.join(STATIC_FOLDER, f))
            )

            if static_files and static_files[-1] != latest_file:
                latest_file = static_files[-1]
                file_path = os.path.join(STATIC_FOLDER, latest_file)
                snapshot_number = extract_snapshot_number(latest_file)

                logging.info(f"[monitor_static_directory] Detected new file: {file_path}")

                process = subprocess.Popen(
                    ['/usr/bin/webtorrent', 'seed', file_path, '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                magnet_url = stream_output(process, eth_address, snapshot_number)

                if magnet_url:
                    logging.info(f"[monitor_static_directory] File {file_path} seeded with magnet: {magnet_url}")
                    while True:
                        try:
                            response = requests.post(
                                "http://localhost:5002/peer_count",
                                json={"magnet_url": magnet_url}
                            )
                            if response.status_code == 200:
                                peer_count = response.json().get("peer_count", 0)
                                logging.info(f"[monitor_static_directory] {magnet_url} has {peer_count} peers")

                                if peer_count > 10:
                                    logging.info(f"[monitor_static_directory] Peer count exceeded. Stopping seeding.")
                                    requests.post(
                                        "http://localhost:5002/stop_seeding",
                                        json={"eth_address": eth_address}
                                    )
                                    break
                        except Exception as e:
                            logging.error(f"[monitor_static_directory] Peer check failed: {e}")
                        time.sleep(10)
                else:
                    logging.error(f"[monitor_static_directory] Failed to generate magnet for {file_path}")

            time.sleep(5)

        except Exception as e:
            logging.error(f"[monitor_static_directory] Error: {e}")
            break

def monitor_hls_directory(eth_address):
    if is_monitoring_hls.get(eth_address):
        logging.info(f"[monitor_hls_directory] Already monitoring HLS for {eth_address}")
        return
    is_monitoring_hls[eth_address] = True
    logging.info(f"[monitor_hls_directory] Starting HLS monitor for {eth_address}")

    latest_file = None

    while True:
        try:
            logging.debug(f"[monitor_hls_directory] Scanning HLS folder for {eth_address}")
            mp4_files = sorted(
                [f for f in os.listdir(HLS_FOLDER)
                 if f.startswith(eth_address) and f.endswith('.mp4')],
                key=lambda f: os.path.getmtime(os.path.join(HLS_FOLDER, f))
            )

            if mp4_files and mp4_files[-1] != latest_file:
                latest_file = mp4_files[-1]
                file_path = os.path.join(HLS_FOLDER, latest_file)
                snapshot_number = extract_snapshot_number(latest_file)

                logging.info(f"[monitor_hls_directory] Detected new snapshot file: {file_path}")

                process = subprocess.Popen(
                    ['/usr/bin/webtorrent', 'seed', file_path,
                     '--announce=wss://tracker.openwebtorrent.com',
                     '--keep-seeding'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                magnet_url = stream_output(process, eth_address, snapshot_number)

                if magnet_url:
                    logging.info(f"[monitor_hls_directory] File {file_path} seeded with magnet: {magnet_url}")
                    while True:
                        try:
                            response = requests.post(
                                "http://localhost:5002/peer_count",
                                json={"magnet_url": magnet_url}
                            )
                            if response.status_code == 200:
                                peer_count = response.json().get("peer_count", 0)
                                logging.info(f"[monitor_hls_directory] {magnet_url} has {peer_count} peers")

                                if peer_count > 10:
                                    logging.info(f"[monitor_hls_directory] Peer threshold exceeded, stopping seeding.")
                                    requests.post(
                                        "http://localhost:5002/stop_seeding",
                                        json={"eth_address": eth_address}
                                    )
                                    break
                        except Exception as e:
                            logging.error(f"[monitor_hls_directory] Peer count check failed: {e}")
                        time.sleep(10)
                else:
                    logging.error(f"[monitor_hls_directory] Failed to seed {file_path}")

            time.sleep(5)

        except Exception as e:
            logging.error(f"[monitor_hls_directory] Error: {e}")
            break


def extract_snapshot_number(filename):
    try:
        parts = filename.split('_snapshot_')
        return int(parts[1].split('.')[0])
    except Exception:
        return 0


@app.route('/convert_to_mp4', methods=['POST'])
def convert_to_mp4():
    logging.info(f"Received request to convert to mp4: {request.json}")

    data = request.get_json()
    eth_address = data.get("eth_address")
    snapshot_index = data.get("snapshot_index", 0)
    m3u8_path = data.get("m3u8_path")

    if not all([eth_address, m3u8_path]):
        return jsonify({"error": "eth_address and m3u8_path are required"}), 400

    if not os.path.exists(m3u8_path):
        return jsonify({"error": f".m3u8 file not found at {m3u8_path}"}), 404

    output_mp4 = os.path.join(HLS_FOLDER, f"{eth_address}_snapshot_{snapshot_index}.mp4")
    logging.info(f"[convert_to_mp4] Converting {m3u8_path} to {output_mp4}")

    try:
        cmd = [
            'ffmpeg', '-i', m3u8_path,
            '-c', 'copy', '-bsf:a', 'aac_adtstoasc',
            '-t', '15',
            output_mp4
        ]
        subprocess.run(cmd, check=True)

        logging.info(f"[convert_to_mp4] Conversion successful, now seeding {output_mp4}")
        process = subprocess.Popen(
            ['/usr/bin/webtorrent', 'seed', output_mp4, '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        magnet_url = stream_output(process, eth_address, snapshot_index)
        if not magnet_url:
            return jsonify({"error": "Failed to retrieve magnet URL"}), 500

        def monitor_peers_later(magnet_url, eth_address):
            while True:
                try:
                    peer_resp = requests.post("http://localhost:5002/peer_count", json={"magnet_url": magnet_url})
                    if peer_resp.ok:
                        peer_count = peer_resp.json().get("peer_count", 0)
                        logging.info(f"[peer_monitor] {magnet_url} has {peer_count} peers")
                        if peer_count > 10:
                            logging.info(f"[peer_monitor] Stopping seeding for {eth_address}")
                            requests.post("http://localhost:5002/stop_seeding", json={"eth_address": eth_address})
                            break
                except Exception as e:
                    logging.error(f"[peer_monitor] Error: {e}")
                time.sleep(10)

        Thread(target=monitor_peers_later, args=(magnet_url, eth_address), daemon=True).start()

        return jsonify({"output_path": output_mp4, "magnet_url": magnet_url}), 200

    except subprocess.CalledProcessError as e:
        logging.error(f"[convert_to_mp4] FFmpeg failed: {e}")
        return jsonify({"error": "FFmpeg conversion failed"}), 500
    except Exception as e:
        logging.error(f"[convert_to_mp4] Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/peer_count', methods=['POST'])
def peer_count():
    data = request.get_json()
    magnet_url = data.get("magnet_url")

    if not magnet_url:
        return jsonify({"error": "magnet_url is required"}), 400

    try:
        cmd = ['/usr/bin/webtorrent', 'info', magnet_url]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        for line in output.splitlines():
            if "Connected to" in line and "peers" in line:
                words = line.split()
                for i, word in enumerate(words):
                    if word == "to" and words[i + 1].isdigit():
                        return jsonify({"peer_count": int(words[i + 1])}), 200

        return jsonify({"peer_count": 0}), 200

    except Exception as e:
        logging.error(f"Failed to get peer count: {e}")
        return jsonify({"error": str(e)}), 500


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

    if 'file' not in request.files:
        logging.error("File not provided in the request.")
        return jsonify({"error": "File is required"}), 400

    eth_address = request.form.get('eth_address')
    if not eth_address or not eth_address.startswith('0x') or len(eth_address) != 42:
        logging.error("Invalid or missing eth_address.")
        return jsonify({"error": "Valid eth_address is required"}), 400

    file = request.files['file']

    if file.filename == '':
        logging.error("No file selected in the request.")
        return jsonify({"error": "No file selected"}), 400

    file_name = file.filename
    file_path = os.path.join(STATIC_FOLDER, file_name)

    # Save the file to disk if not already saved
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
    seed_processes[eth_address] = process  # ✅ Save process reference for stopping

    

    magnet_url = stream_output(process, eth_address, snapshot_index=0)


    if magnet_url:
        return jsonify({"magnet_url": magnet_url}), 200
    else:
        return jsonify({"error": "Failed to seed file and retrieve magnet URL"}), 500

@app.route('/stop_seeding', methods=['POST'])
def stop_seeding():
    data = request.get_json()
    eth_address = data.get("eth_address")

    if not eth_address:
        return jsonify({"error": "eth_address is required"}), 400

    process = seed_processes.get(eth_address)
    if not process:
        return jsonify({"error": f"No seeding process found for {eth_address}"}), 404

    try:
        process.terminate()
        process.wait(timeout=5)
        del seed_processes[eth_address]
        logging.info(f"Seeding process for {eth_address} has been stopped.")
        return jsonify({"message": f"Seeding stopped for {eth_address}"}), 200
    except Exception as e:
        logging.error(f"Failed to stop seeding for {eth_address}: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logging.info("Starting Flask server...")
    #seed_all_static_files()
    app.run(host='0.0.0.0', port=5002, debug=True, ssl_context=('/certs/fullchain.pem', '/certs/privkey.pem'))
