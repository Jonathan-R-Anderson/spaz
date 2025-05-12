from shared import (
    User, MagnetURL, db, HMAC_SECRET_KEY, logging, app,
    blueprint
)
from app import (_clear_magnet_urls, _generate_secret, _hash_secret,
                 _store_secret, _store_magnet_url, _fetch_secret_from_api)
from flask import request, jsonify
import hmac

@blueprint.route('/get_secret/<eth_address>', methods=['GET'])
def get_secret(eth_address):
    logging.info(f"[get_secret] Received request to fetch secret for: {eth_address}")
    try:
        user = User.query.filter_by(eth_address=eth_address).first()
        if user:
            logging.info(f"[get_secret] Secret found for {eth_address}")
            return jsonify({"eth_address": eth_address, "secret": user.rtmp_secret}), 200
        else:
            logging.warning(f"[get_secret] No secret found for {eth_address}")
            return jsonify({"error": "Secret not found"}), 404
    except Exception as e:
        logging.error(f"[get_secret] Failed to fetch secret for {eth_address}: {e}")
        return jsonify({"error": "Internal server error"}), 500



@blueprint.route('/get_magnet_urls/<eth_address>', methods=['GET'])
def retrieve_magnet_urls(eth_address):
    urls = MagnetURL.query.filter_by(eth_address=eth_address).order_by(MagnetURL.snapshot_index).all()
    logging.info(f"data from db {urls}")
    if urls:
        return jsonify({
            "message": "success",
            "eth_address": eth_address,
            "magnet_urls": [
                {"magnet_url": url.magnet_url, "snapshot_index": url.snapshot_index, "created_at": url.created_at}
                for url in urls
            ]
        }), 200
    else:
        return jsonify({"message": "failure"}), 500 

# API to generate and store a new secret
@blueprint.route('/generate_secret', methods=['POST'])
def generate_and_store_secret():
    logging.info("===== [START] /generate_secret =====")

    try:
        data = request.get_json()
        logging.info(f"Incoming JSON payload: {data}")

        eth_address = data.get('eth_address') if data else None
        ip_address = data.get('ip_address') if data else None

        if not eth_address:
            logging.warning("Missing Ethereum address in request.")
            return jsonify({"error": "Missing Ethereum address"}), 400

        if not ip_address:
            logging.warning("Missing IP address in request.")
            return jsonify({"error": "Missing IP address"}), 400

        logging.info(f"Generating secret for eth_address: {eth_address}, ip_address: {ip_address}")
        secret = _generate_secret()
        logging.info(f"Generated plaintext secret: {secret}")

        logging.info("Storing secret in database...")
        _store_secret(eth_address, secret, ip_address)
        logging.info("Successfully stored secret in DB.")

        logging.info("===== [END] /generate_secret =====")
        return jsonify({"eth_address": eth_address, "secret": secret}), 200

    except Exception as e:
        logging.exception(f"Unhandled exception in /generate_secret: {e}")
        return jsonify({"error": "Internal server error"}), 500


@blueprint.route('/get_rtmp_url/<eth_address>', methods=['GET'])
def get_rtmp_url(eth_address):
    logging.info(f"[get_rtmp_url] Received request to build RTMP URL for: {eth_address}")
    try:
        user = User.query.filter_by(eth_address=eth_address).first()
        if user:
            secret = user.rtmp_secret
            rtmp_url = f"rtmp://psichos.is:1935/live/{eth_address}?secret={secret}"
            logging.info(f"[get_rtmp_url] Returning RTMP URL: {rtmp_url}")
            return jsonify({"rtmp_url": rtmp_url}), 200
        else:
            logging.warning(f"[get_rtmp_url] No user found for {eth_address}")
            return jsonify({"error": "Secret not found"}), 404
    except Exception as e:
        logging.error(f"[get_rtmp_url] Exception while fetching RTMP URL: {e}")
        return jsonify({"error": "Internal server error"}), 500


# API to store a magnet URL
@blueprint.route('/store_magnet_url', methods=['POST'])
def store_magnet_url_route():
    data = request.json
    eth_address = data.get('eth_address')
    magnet_url = data.get('magnet_url')
    snapshot_index = data.get('snapshot_index')

    if not eth_address or not magnet_url or snapshot_index is None:
        return jsonify({"error": "Missing required fields"}), 400

    return _store_magnet_url(eth_address, magnet_url, snapshot_index)




# API to clear all magnet URLs for a specific eth_address
@blueprint.route('/clear_magnet_urls/<eth_address>', methods=['DELETE'])
def clear_magnet_urls_route(eth_address):
    return _clear_magnet_urls(eth_address)


# API to store streamer information (eth_address, secret, and IP address)
@blueprint.route('/store_streamer_info', methods=['POST'])
def store_streamer_info():
    data = request.json
    eth_address = data.get('eth_address')
    secret = data.get('secret')
    ip_address = data.get('ip_address')

    logging.info(f"Storing streamer info: eth_address={eth_address}, secret={secret}, ip_address={ip_address}")


    if not eth_address or not secret or not ip_address:
        return jsonify({"error": "Missing required fields"}), 400


    try:
        # Store or update the streamer information in the PostgreSQL database
        user = User.query.filter_by(eth_address=eth_address).first()
        if user:
            # Update the existing record with the new secret and ip_address
            user.rtmp_secret = secret
            # Assuming you have an IP column in the database
            user.ip_address = ip_address  # You would need to add this field in the model
        else:
            # Create a new user record if it doesn't exist
            user = User(eth_address, secret)
            user.ip_address = ip_address  # Set the IP address

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Streamer info stored successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to store streamer info: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to store streamer info"}), 500

# API to get the streamer's IP address based on their Ethereum address
@blueprint.route('/get_streamer_eth_address/<ip_address>', methods=['GET'])
def get_streamer_ip(ip_address):
    try:
        # Query the database for the user based on the Ethereum address
        user = User.query.filter_by(ip_address=ip_address).first()

        if user:
            # Return the IP address if the user is found
            return jsonify({"eth_address": user.eth_address, "ip_address": user.ip_address}), 200
        else:
            # Return an error if the user is not found
            return jsonify({"error": f"No streamer found with Ethereum address: {ip_address}"}), 404
    except Exception as e:
        logging.error(f"Failed to retrieve IP address for {ip_address}: {str(e)}")
        return jsonify({"error": "Failed to retrieve IP address"}), 500

@blueprint.route('/verify_secret', methods=['POST'])
def verify_secret():
    if request.is_json:
        eth_address = request.json.get('eth_address')
        secret = request.json.get('secret')
    else:
        stream_key = request.args.get('name') or request.form.get('name')
        if not stream_key or '&' not in stream_key:
            return '', 403
        try:
            eth_address, secret = stream_key.split('&secret=')
        except Exception:
            return '', 403

    if not eth_address or not secret:
        return '', 403

    stored_secret = _fetch_secret_from_api(eth_address)
    if not stored_secret:
        return '', 403

    if hmac.compare_digest(secret, stored_secret):
        return '', 204
    else:
        return '', 403


app.register_blueprint(blueprint)
