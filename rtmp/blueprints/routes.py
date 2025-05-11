from shared import (logging, retrieve_magnet_urls, requests, jsonify,
                    WEBTORRENT_CONTAINER_URL, request, STATIC_FOLDER,
                    os, seeded_files, PROFILE_DB_URL, hmac, Process,
                    seed_all_static_files_for_user, app)


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
                f"{WEBTORRENT_CONTAINER_URL}/start_static_monitor",
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
                f"{WEBTORRENT_CONTAINER_URL}/start_hls_monitor",
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
            response = requests.post(f"{WEBTORRENT_CONTAINER_URL}/seed", files=files, data=data)

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
            f"{PROFILE_DB_URL}/store_streamer_info",
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
        secret_response = requests.get(f"{PROFILE_DB_URL}/get_secret/{eth_address}", timeout=5)
        if secret_response.status_code != 200:
            logging.warning(f"[verify_secret] No stored secret found for {eth_address}")
            return '', 403

        stored_secret = secret_response.json().get('secret')
    except Exception as e:
        logging.error(f"[verify_secret] Exception retrieving stored secret: {e}")
        return '', 500

    if hmac.compare_digest(secret, stored_secret):
        logging.info(f"[verify_secret] ✅ Secret verified for {eth_address}")
        p = Process(target=seed_all_static_files_for_user, args=(eth_address,))
        p.start()
        
        return '', 204
    else:
        logging.warning(f"[verify_secret] ❌ Secret mismatch for {eth_address}")
        return '', 403
