import logging
from flask import Blueprint, request, jsonify
from multiprocessing import Process
import os
from config import Config
from api.services.monitor import start_monitoring
from utils.files import is_valid_eth_address
from config import Config
import re
from api.services.monitor import (
    monitor_static_directory,
    monitor_hls_directory,
    retrieve_magnet_urls,
    stream_output
)
import subprocess
import requests
from config import Config

blueprint = Blueprint("webtorrent", __name__)
UPLOAD_DIR = Config.UPLOAD_DIR
DATABASE_API = f"{Config.DATABASE_URI}:{Config.DATABASE_PORT}"


@blueprint.route('/start_static_monitor', methods=['POST'])
def start_static_monitor():
    data = request.get_json()
    eth_address = data.get('eth_address')

    if not eth_address:
        return jsonify({"error": "eth_address is required"}), 400

    if Config.is_monitoring_static.get(eth_address):
        logging.info(f"[API] Static monitor already running for {eth_address}")
        return jsonify({"message": "Static monitor already running"}), 200

    logging.info(f"[API] Starting static monitor for {eth_address}")
    try:
        process = Process(target=monitor_static_directory, args=(eth_address,))
        process.start()
        return jsonify({"message": "Static monitor started"}), 200
    except Exception as e:
        logging.error(f"[API] Failed to start static monitor: {e}")
        return jsonify({"error": "Failed to start static monitor"}), 500

@blueprint.route('/start_hls_monitor', methods=['POST'])
def start_hls_monitor():
    data = request.get_json()
    eth_address = data.get('eth_address')

    if not eth_address:
        return jsonify({"error": "eth_address is required"}), 400

    if Config.is_monitoring_hls.get(eth_address):
        logging.info(f"[API] HLS monitor already running for {eth_address}")
        return jsonify({"message": "HLS monitor already running"}), 200

    logging.info(f"[API] Starting HLS monitor for {eth_address}")
    try:
        process = Process(target=monitor_hls_directory, args=(eth_address,))
        process.start()
        return jsonify({"message": "HLS monitor started"}), 200
    except Exception as e:
        logging.error(f"[API] Failed to start HLS monitor: {e}")
        return jsonify({"error": "Failed to start HLS monitor"}), 500


@blueprint.route('/convert_to_mp4', methods=['POST'])
def convert_to_mp4():
    logging.info(f"[convert_to_mp4] Received request: {request.json}")

    data = request.get_json()
    eth_address = data.get("eth_address")
    snapshot_index = data.get("snapshot_index", 0)
    filename = data.get("filename")

    if not all([eth_address, filename]):
        return jsonify({"error": "eth_address and filename are required"}), 400

    # Decode and sanitize filename by removing &secret=...
    decoded_filename = unquote(filename)
    sanitized_filename = re.sub(r"&secret=.*", "", decoded_filename)

    # Construct full path to .m3u8
    m3u8_path = os.path.join(Config.HLS_FOLDER, sanitized_filename)

    if not os.path.exists(m3u8_path):
        logging.error(f"[convert_to_mp4] .m3u8 file not found at: {m3u8_path}")
        return jsonify({"error": f".m3u8 file not found at {m3u8_path}"}), 404

    output_mp4 = os.path.join(Config.HLS_FOLDER, f"{eth_address}_snapshot_{snapshot_index}.mp4")
    logging.info(f"[convert_to_mp4] Converting {m3u8_path} to {output_mp4}")

    try:
        cmd = [
            'ffmpeg', '-i', m3u8_path,
            '-c', 'copy', '-bsf:a', 'aac_adtstoasc',
            '-t', '15',
            output_mp4
        ]
        subprocess.run(cmd, check=True)

        logging.info(f"[convert_to_mp4] Conversion successful, seeding {output_mp4}")
        process = subprocess.Popen(
            ['/usr/bin/webtorrent', 'seed', output_mp4,
             '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
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
                            logging.info(f"[peer_monitor] Peer threshold reached, stopping seeding.")
                            requests.post("http://localhost:5002/stop_seeding", json={"eth_address": eth_address})
                            break
                except Exception as e:
                    logging.error(f"[peer_monitor] Error monitoring peers: {e}")
                time.sleep(10)

        Thread(target=monitor_peers_later, args=(magnet_url, eth_address), daemon=True).start()

        return jsonify({"output_path": output_mp4, "magnet_url": magnet_url}), 200

    except subprocess.CalledProcessError as e:
        logging.error(f"[convert_to_mp4] FFmpeg failed: {e}")
        return jsonify({"error": "FFmpeg conversion failed"}), 500
    except Exception as e:
        logging.error(f"[convert_to_mp4] Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500
    
@blueprint.route('/peer_count', methods=['POST'])
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


@blueprint.route('/magnet_urls/<eth_address>', methods=['GET'])
def magnet_url(eth_address):
    logging.info(f"Received request for magnet URLs for Ethereum address: {eth_address}")

    logging.info(f"Attempting to retrieve magnet URLs for {eth_address} from DATABASE_URL API.")
    magnet_urls = retrieve_magnet_urls(eth_address)
    logging.info(f"Response from DATABASE_URL for {eth_address}: {magnet_urls}")
    
    if magnet_urls.get("message") == "success":
        logging.info(f"Successfully retrieved magnet URLs for {eth_address}. Returning URLs.")
        return jsonify({"magnet_urls": magnet_urls.get("magnet_urls")}), 200
    else:
        logging.warning(f"Magnet URLs not found for {eth_address}. Initiating directory monitoring.")

        if not Config.is_monitoring_static.get(eth_address, None):
            try:
                logging.info(f"Starting process to monitor static directory for {eth_address}.")
                static_process = Process(target=monitor_static_directory, args=(eth_address,))
                static_process.start()
                Config.is_monitoring_static[eth_address] = True
                logging.info(f"Successfully started monitoring static directory for {eth_address}.")
            except Exception as e:
                logging.error(f"Error starting static directory monitoring for {eth_address}: {e}")
                return jsonify({"error": "Failed to monitor static directory"}), 500

        if not Config.is_monitoring_hls.get(eth_address, None):
            try:
                logging.info(f"Starting process to monitor HLS directory for {eth_address}.")
                hls_process = Process(target=monitor_hls_directory, args=(eth_address,))
                hls_process.start()
                Config.is_monitoring_hls[eth_address] = True
                logging.info(f"Successfully started monitoring HLS directory for {eth_address}.")
            except Exception as e:
                logging.error(f"Error starting HLS directory monitoring for {eth_address}: {e}")
                return jsonify({"error": "Failed to monitor HLS directory"}), 500

        logging.error(f"Magnet URL not found for {eth_address} and monitoring started.")
        return jsonify({"error": "Magnet URL not found and monitoring started"}), 404

@blueprint.route('/seed', methods=['POST'])
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
    file_path = os.path.join(Config.HLS_DIR, file_name)

    # Save the file to disk if not already saved
    if not os.path.exists(file_path):
        file.save(file_path)
        logging.info(f"Saved uploaded file to {file_path}")
    else:
        logging.info(f"File {file_path} already exists on disk.")

    if file_path in Config.seeded_files:
        logging.info(f"File {file_name} is already seeded.")
        magnet_url = Config.seeded_files[file_path]
        return jsonify({"magnet_url": magnet_url}), 200

    logging.info(f"Seeding file {file_path}...")

    process = subprocess.Popen(
        ['/usr/bin/webtorrent', 'seed', file_path, '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    Config.seed_processes[eth_address] = process  

    magnet_url = stream_output(process, eth_address, snapshot_index=0)


    if magnet_url:
        return jsonify({"magnet_url": magnet_url}), 200
    else:
        return jsonify({"error": "Failed to seed file and retrieve magnet URL"}), 500

@blueprint.route("/add_file", methods=["POST"])
def add_file():
    file = request.files['file']
    group_id = request.form.get('group_id')

    if not os.path.exists(Config.UPLOAD_DIR):
        os.makedirs(Config.UPLOAD_DIR)

    if not group_id:
        resp = requests.post(f"{DATABASE_API}/create_group")
        if not resp.ok:
            return jsonify({"error": "Failed to create group"}), 500
        group_id = resp.json()["group_id"]

    group_path = os.path.join(Config.UPLOAD_DIR, str(group_id))
    os.makedirs(group_path, exist_ok=True)

    file_path = os.path.join(group_path, secure_filename(file.filename))
    file.save(file_path)

    # Calculate hash
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    file_hash = sha256.hexdigest()

    relative_path = os.path.relpath(file_path, Config.UPLOAD_DIR)

    resp = requests.post(f"{DATABASE_API}/add_file_to_group", json={
        "group_id": group_id,
        "file_path": relative_path,
        "file_hash": file_hash
    })
    if not resp.ok:
        return jsonify({"error": "Failed to register file"}), 500

    return jsonify({"status": "ok", "group_id": group_id, "file_hash": file_hash})


@blueprint.route("/finalize_snapshot/<int:group_id>", methods=["POST"])
def finalize_snapshot(group_id):
    group_path = os.path.join(Config.UPLOAD_DIR, str(group_id))
    if not os.path.exists(group_path):
        return jsonify({"error": "group not found"}), 404

    torrent_path, magnet_uri, file_hashes = create_torrent(group_path)

    # Update metadata via database API
    for filename, hash_val in file_hashes.items():
        requests.post(f"{DATABASE_API}/update_file_metadata", json={
            "group_id": group_id,
            "file_path": filename,
            "file_hash": hash_val,
            "magnet_url": magnet_uri
        })

    return jsonify({
        "group_id": group_id,
        "magnet": magnet_uri,
        "torrent_path": torrent_path,
        "files": file_hashes
    })


@blueprint.route("/get_snapshot/<int:group_id>", methods=["GET"])
def get_snapshot(group_id):
    resp = requests.get(f"{DATABASE_API}/get_group_files/{group_id}")
    if not resp.ok:
        return jsonify({"error": "Failed to retrieve group"}), 500
    return jsonify(resp.json())


@blueprint.route("/update_snapshot/<int:group_id>", methods=["POST"])
def update_snapshot(group_id):
    return finalize_snapshot(group_id)


@blueprint.route("/list_snapshots", methods=["GET"])
def list_snapshots():
    resp = requests.get(f"{DATABASE_API}/list_snapshots")
    return jsonify(resp.json())