from flask import request, jsonify
from api.routes import blueprint
from services import (
    _clear_magnet_urls, _generate_secret, _hash_secret,
    _store_secret, _store_magnet_url, 
)
import hmac


from extensions import db
from models.user import Users
from models.magnet import MagnetURL
from system.logging import setup_logger
from flask import Blueprint, request, jsonify
from models import db, TorrentGroup, TorrentFile

logger = setup_logger(__name__)


@blueprint.route('/get_secret/<eth_address>', methods=['GET'])
def get_secret(eth_address):
    logger.info(f"[get_secret] Received request to fetch secret for: {eth_address}")
    try:
        user = Users.query.filter_by(eth_address=eth_address).first()
        if user:
            logger.info(f"[get_secret] Secret found for {eth_address}")
            return jsonify({
                "eth_address": eth_address,
                "secret": user.rtmp_secret
            }), 200
        else:
            logger.warning(f"[get_secret] No secret found for {eth_address}")
            return jsonify({"error": "Secret not found"}), 404
    except Exception as e:
        logger.error(f"[get_secret] Failed to fetch secret for {eth_address}: {e}")
        return jsonify({"error": "Internal server error"}), 500




@blueprint.route('/get_magnet_urls/<eth_address>', methods=['GET'])
def retrieve_magnet_urls(eth_address):
    urls = MagnetURL.query.filter_by(eth_address=eth_address).order_by(MagnetURL.snapshot_index).all()
    logger.info(f"data from db {urls}")
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

@blueprint.route('/generate_secret', methods=['POST'])
def generate_and_store_secret():
    import sys
    sys.stderr.write("=== HIT /generate_secret route ===\n")
    sys.stderr.flush()

    try:
        data = request.get_json(force=True)
        print(f"== JSON received: {data}")
        eth_address = data.get('eth_address')
        ip_address = data.get('ip_address')

        print(f"eth_address: {eth_address}, ip_address: {ip_address}")

        secret = _generate_secret()
        print(f"generated secret: {secret}")

        _store_secret(eth_address, secret, ip_address)
        print("stored secret successfully")

        return jsonify({"eth_address": eth_address, "secret": secret}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500



@blueprint.route('/get_rtmp_url/<eth_address>', methods=['GET'])
def get_rtmp_url(eth_address):
    logger.info(f"[get_rtmp_url] Received request to build RTMP URL for: {eth_address}")
    try:
        user = Users.query.filter_by(eth_address=eth_address).first()
        if user:
            secret = user.rtmp_secret
            rtmp_url = f"rtmp://psichos.is:1935/live/{eth_address}?secret={secret}"
            logger.info(f"[get_rtmp_url] Returning RTMP URL: {rtmp_url}")
            return jsonify({"rtmp_url": rtmp_url}), 200
        else:
            logger.warning(f"[get_rtmp_url] No user found for {eth_address}")
            return jsonify({"error": "Secret not found"}), 404
    except Exception as e:
        logger.error(f"[get_rtmp_url] Exception while fetching RTMP URL: {e}")
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

    logger.info(f"Storing streamer info: eth_address={eth_address}, secret={secret}, ip_address={ip_address}")


    if not eth_address or not secret or not ip_address:
        return jsonify({"error": "Missing required fields"}), 400


    try:
        # Store or update the streamer information in the PostgreSQL database
        user = Users.query.filter_by(eth_address=eth_address).first()
        if user:
            # Update the existing record with the new secret and ip_address
            user.rtmp_secret = secret
            # Assuming you have an IP column in the database
            user.ip_address = ip_address  # You would need to add this field in the model
        else:
            # Create a new user record if it doesn't exist
            user = Users(eth_address, secret)
            user.ip_address = ip_address  # Set the IP address

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Streamer info stored successfully"}), 200
    except Exception as e:
        logger.error(f"Failed to store streamer info: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to store streamer info"}), 500

# API to get the streamer's IP address based on their Ethereum address
@blueprint.route('/get_streamer_eth_address/<ip_address>', methods=['GET'])
def get_streamer_ip(ip_address):
    try:
        # Query the database for the user based on the Ethereum address
        user = Users.query.filter_by(ip_address=ip_address).first()

        if user:
            # Return the IP address if the user is found
            return jsonify({"eth_address": user.eth_address, "ip_address": user.ip_address}), 200
        else:
            # Return an error if the user is not found
            return jsonify({"error": f"No streamer found with Ethereum address: {ip_address}"}), 404
    except Exception as e:
        logger.error(f"Failed to retrieve IP address for {ip_address}: {str(e)}")
        return jsonify({"error": "Failed to retrieve IP address"}), 500

@blueprint.route('/verify_secret', methods=['POST'])
def verify_secret_fun():
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
            return '', 402

    if not eth_address or not secret:
        return '', 401

    user = Users.query.filter_by(eth_address=eth_address).first()
    if not user:
        return '', 400

    if hmac.compare_digest(secret, user.rtmp_secret):
        return '', 204
    return '', 403

@blueprint.route("/create_group", methods=["POST"])
def create_group():
    group = TorrentGroup()
    db.session.add(group)
    db.session.commit()
    return jsonify({"group_id": group.id})

@blueprint.route("/add_file_to_group", methods=["POST"])
def add_file_to_group():
    data = request.get_json()
    file = TorrentFile(
        group_id=data["group_id"],
        file_path=data["file_path"],
        file_hash=data["file_hash"]
    )
    db.session.add(file)
    db.session.commit()
    return jsonify({"message": "File registered"})

@blueprint.route("/update_file_metadata", methods=["POST"])
def update_file_metadata():
    data = request.get_json()
    file = TorrentFile.query.filter_by(
        group_id=data["group_id"],
        file_path=data["file_path"]
    ).first()
    if not file:
        return jsonify({"error": "File not found"}), 404

    file.file_hash = data["file_hash"]
    file.magnet_url = data["magnet_url"]
    db.session.commit()
    return jsonify({"message": "Metadata updated"})

@blueprint.route("/get_group_files/<int:group_id>", methods=["GET"])
def get_group_files(group_id):
    files = TorrentFile.query.filter_by(group_id=group_id).all()
    return jsonify([
        {
            "file_path": f.file_path,
            "file_hash": f.file_hash,
            "magnet_url": f.magnet_url
        } for f in files
    ])

@blueprint.route("/list_snapshots", methods=["GET"])
def list_snapshots():
    groups = TorrentGroup.query.all()
    return jsonify([
        {
            "group_id": g.id,
            "created_at": g.created_at.isoformat(),
            "updated_at": g.updated_at.isoformat()
        } for g in groups
    ])

# Expose route logic functions for direct use in unit tests
__all__ = [
    "generate_and_store_secret",
    "get_secret",
    "get_rtmp_url",
    "retrieve_magnet_urls",
    "store_magnet_url_route",
    "clear_magnet_urls_route",
    "store_streamer_info",
    "get_streamer_ip",
    "verify_secret_fun"
]
