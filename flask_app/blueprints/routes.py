from flask import Blueprint, render_template, request, jsonify, send_from_directory
from shared import (
    gremlinThreadABI, gremlinThreadAddress,
    gremlinAdminABI, gremlinAdminAddress,
    gremlinReplyABI, gremlinReplyAddress,
    allowed_file, FILE_DIR, save_whitelist,
    save_blacklist, blacklist, whitelist,
    app, gremlinProfileAddress, gremlinProfileABI,
    client, WEBTORRENT_CONTAINER_URL,
    HMAC_SECRET_KEY, session_store, generate_ecc_key_pair,
    serialize_public_key, RTMP_URLS, DB_API_URL, LOG_FILE_PATH,
    gremlinChallengeABI, gremlinChallengeAddress,
    gremlinDAOABI, gremlinDAOAddress,
    gremlinLeaderboardABI, gremlinLeaderboardAddress,
    gremlinJournalABI, gremlinJournalAddress
)
import json, os, logging, hmac, hashlib, base64, requests, subprocess
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

blueprint = Blueprint('blueprint', __name__)

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

SECURE_MESSAGE = "Please sign this message to verify ownership of your Ethereum address."

@blueprint.route('/')
def index():
    logging.debug("Rendering welcome page.")
    return render_template('welcome.html')

@blueprint.route('/dashboard/<eth_address>', methods=['GET'])
def home(eth_address):
    logging.debug(f"Rendering dashboard for {eth_address}")
    return render_template('dashboard.html', eth_address=eth_address,
                           gremlinProfileABI=json.dumps(gremlinProfileABI, ensure_ascii=False),
                           gremlinProfileAddress=gremlinProfileAddress,
                           gremlinLeaderboardAddress=gremlinLeaderboardAddress,
                           gremlinLeaderboardABI=json.dumps(gremlinLeaderboardABI, ensure_ascii=False),
                           gremlinJournalAddress=gremlinJournalAddress,
                           gremlinJournalABI=json.dumps(gremlinJournalABI, ensure_ascii=False))

@app.route('/get_rtmp_url/<eth_address>', methods=['GET'])
def get_rtmp_url(eth_address):
    from shared import DB_API_URL  # Make sure DB_API_URL is set correctly (e.g., https://psichos.is:5003)

    logging.info(f"[proxy_get_rtmp_url] Incoming request for eth_address: {eth_address}")

    try:
        # Construct full URL to DB container's endpoint
        db_url = f"{DB_API_URL}/get_rtmp_url/{eth_address}"
        logging.info(f"[proxy_get_rtmp_url] Forwarding to DB URL: {db_url}")

        # Send GET request to DB container
        response = requests.get(db_url, timeout=10)

        # Log and forward response
        logging.info(f"[proxy_get_rtmp_url] DB response status: {response.status_code}")
        logging.debug(f"[proxy_get_rtmp_url] DB response content: {response.text}")

        return (response.text, response.status_code, {'Content-Type': 'application/json'})

    except requests.exceptions.RequestException as e:
        logging.error(f"[proxy_get_rtmp_url] Error while contacting DB: {str(e)}")
        return jsonify({"error": "Failed to contact DB"}), 500

@app.route('/css/<filename>')
def serve_css(filename):
    logging.debug(f"Serving CSS file: {filename}")
    return send_from_directory(os.path.join('hosted', 'css'), filename)

@app.route('/js/<filename>')
def serve_js(filename):
    logging.debug(f"Serving JS file: {filename}")
    return send_from_directory(os.path.join('hosted', 'js'), filename)

@app.route('/admin/blacklist/<item_type>', methods=['POST'])
def add_to_blacklist(item_type):
    data = request.json
    item_value = data.get(item_type)
    logging.info(f"Adding {item_type}: {item_value} to blacklist")
    if item_type in ['tag', 'magnet', 'user']:
        key = f"{item_type}s"
        if item_value not in blacklist[key]:
            blacklist[key].append(item_value)
            save_blacklist(blacklist)
            return jsonify({"message": f"{item_type.capitalize()} '{item_value}' added to blacklist"}), 200
        return jsonify({"error": f"{item_type.capitalize()} already blacklisted"}), 400
    return jsonify({"error": "Invalid blacklist type"}), 400

@app.route('/admin/whitelist/<item_type>', methods=['POST'])
def add_to_whitelist(item_type):
    data = request.json
    item_value = data.get(item_type)
    logging.info(f"Adding {item_type}: {item_value} to whitelist")
    if item_type in ['tag', 'magnet', 'user']:
        key = f"{item_type}s"
        if item_value not in whitelist[key]:
            whitelist[key].append(item_value)
            save_whitelist(whitelist)
            return jsonify({"message": f"{item_type.capitalize()} '{item_value}' added to whitelist"}), 200
        return jsonify({"error": f"{item_type.capitalize()} already whitelisted"}), 400
    return jsonify({"error": "Invalid whitelist type"}), 400

@app.route('/admin/blacklist')
def get_blacklist():
    logging.info("Retrieving blacklist")
    return jsonify(blacklist)

@app.route('/admin/whitelist')
def get_whitelist():
    logging.info("Retrieving whitelist")
    return jsonify(whitelist)

@app.route('/users/<eth_address>', methods=['POST', 'GET'])
def user_profile(eth_address):
    if request.method == 'POST':
        current_user_eth_address = request.json.get('current_user_eth_address')
        is_owner = current_user_eth_address.lower() == eth_address.lower()
        rtmp_url = RTMP_URLS.get(eth_address, "psichos.is") if is_owner else "psichos.is"
        logging.debug(f"Profile POST for {eth_address}, owner={is_owner}")
        return jsonify({"is_owner": is_owner, "rtmp_stream_url": rtmp_url})
    logging.debug(f"Rendering profile for {eth_address}")
    return render_template('profile.html', eth_address=eth_address,
                           gremlinProfileABI=json.dumps(gremlinProfileABI, ensure_ascii=False),
                           gremlinProfileAddress=gremlinProfileAddress,
                           gremlinLeaderboardAddress=gremlinLeaderboardAddress,
                           gremlinLeaderboardABI=json.dumps(gremlinLeaderboardABI, ensure_ascii=False),
                           gremlinJournalAddress=gremlinJournalAddress,
                           gremlinJournalABI=json.dumps(gremlinJournalABI, ensure_ascii=False))

@app.route('/generate_rtmp_url', methods=['POST'])
def generate_rtmp_url():
    logging.info("Generating RTMP URL")
    eth_address = request.json.get('eth_address')
    ip_address = request.json.get('ip_address')
    if not eth_address:
        logging.warning("Missing Ethereum address")
        return jsonify({"error": "Ethereum address is required"}), 400
    try:
        response = requests.post(f"{DB_API_URL}/generate_secret", json={"eth_address": eth_address, "ip_address": ip_address}, timeout=30)
        logging.debug(f"Secret generation response: {response.status_code} - {response.text}")
        if response.status_code != 200:
            return jsonify({"error": "Failed to generate secret"}), 500
        new_secret = response.json().get('secret')
        rtmp_url = f"rtmp://psichos.is:1935/live/{eth_address}?secret={new_secret}"
        return jsonify({"new_rtmp_url": rtmp_url}), 200
    except Exception as e:
        logging.exception("Error generating RTMP URL")
        return jsonify({"error": str(e)}), 500

@app.route('/magnet_urls/<eth_address>')
def get_magnet_url(eth_address):
    logging.info(f"Fetching magnet URLs for {eth_address}")
    try:
        response = requests.get(f"{WEBTORRENT_CONTAINER_URL}/magnet_urls/{eth_address}", timeout=30, verify=False)
        if response.status_code == 200:
            return jsonify({"magnet_urls": response.json().get("magnet_urls")}), 200
        return jsonify({"error": "Failed to generate magnet URLs"}), 500
    except Exception as e:
        logging.exception("WebTorrent communication error")
        return jsonify({"error": str(e)}), 500

@app.route('/start_session', methods=['POST'])
def start_session():
    eth_address = request.json.get('eth_address')
    logging.debug(f"Starting session for {eth_address}")
    if not eth_address:
        return jsonify({"error": "Ethereum address missing"}), 400
    private_key, public_key = generate_ecc_key_pair()
    session_store[eth_address] = private_key
    return jsonify({"eth_address": eth_address, "public_key": serialize_public_key(public_key)}), 200

@app.route('/verify', methods=['POST'])
def verify_hmac():
    eth_address = request.json.get('eth_address')
    encrypted_hmac = request.json.get('encrypted_hmac')
    logging.debug(f"Verifying HMAC for {eth_address}")
    if not eth_address or not encrypted_hmac:
        return jsonify({"error": "Missing Ethereum address or encrypted HMAC"}), 400
    private_key = session_store.get(eth_address)
    if not private_key:
        return jsonify({"error": "Session expired or invalid"}), 400
    try:
        encrypted_hmac_bytes = base64.b64decode(encrypted_hmac)
        hmac_secret = private_key.decrypt(encrypted_hmac_bytes, ec.ECIESHKDF(salt=None, algorithm=hashes.SHA256()))
        hmac_secret = hmac_secret.decode('utf-8')
    except Exception as e:
        logging.exception("Decryption failed")
        return jsonify({"error": "Decryption failed"}), 500
    calculated_hmac = hmac.new(HMAC_SECRET_KEY.encode(), eth_address.encode(), hashlib.sha256).hexdigest()
    if hmac.compare_digest(calculated_hmac, hmac_secret):
        return jsonify({"message": "HMAC verified successfully"}), 200
    return jsonify({"error": "HMAC verification failed"}), 401


@app.route('/verify_secret', methods=['GET'])
def verify_secret():
    logging.info("[verify_secret] Received verification request")

    stream_key = request.args.get("name")  # whole string: 0xabc...&secret=xyz
    ip_address = request.remote_addr

    logging.info(f"[verify_secret] Incoming raw stream_key: {stream_key} from {ip_address}")

    if not stream_key or '&' not in stream_key:
        logging.warning("[verify_secret] Malformed stream key")
        return '', 403

    try:
        parts = dict(q.split('=') for q in stream_key.split('&'))
        eth_address = next(k for k in parts if k.startswith("0x"))
        secret = parts.get('secret')
    except Exception as e:
        logging.error(f"[verify_secret] Failed to parse stream key: {e}")
        return '', 403

    if not eth_address or not secret:
        logging.warning("[verify_secret] Missing eth_address or secret after parsing")
        return '', 403

    # Call internal verification
    verify_response = requests.post(
        f"http://profile_db:5003/verify_secret",
        json={"eth_address": eth_address, "secret": secret},
        timeout=10,
    )

    if verify_response.status_code == 200:
        logging.info(f"[verify_secret] ✅ Verified {eth_address}")
        return '', 204
    else:
        logging.warning(f"[verify_secret] ❌ Verification failed for {eth_address}")
        return '', 403
