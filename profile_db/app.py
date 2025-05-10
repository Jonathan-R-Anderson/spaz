import os
import hashlib
import hmac
import redis
import random
import requests
import string
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize Flask app
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# Redis client to store secrets (NoSQL key-value store)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost/profile_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Secret key for HMAC hashing (stored in environment variable or use a default)
HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')

# Define a user model for PostgreSQL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eth_address = db.Column(db.String(42), unique=True, nullable=False)
    rtmp_secret = db.Column(db.String(64), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # Ensure this field is added

    def __init__(self, eth_address, rtmp_secret, ip_address):
        self.eth_address = eth_address
        self.rtmp_secret = rtmp_secret
        self.ip_address = ip_address

# Define a model for storing magnet URLs
class MagnetURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eth_address = db.Column(db.String(42), nullable=False)
    magnet_url = db.Column(db.Text, nullable=False)
    snapshot_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Function to clear all magnet URLs associated with an eth_address
def clear_magnet_urls(eth_address):
    try:
        # Query to delete all entries related to the eth_address
        MagnetURL.query.filter_by(eth_address=eth_address).delete()
        db.session.commit()
        return {"message": f"All magnet URLs for {eth_address} have been cleared."}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to clear magnet URLs: {str(e)}"}, 500

# Generate a random secret for RTMP stream
def generate_secret():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Hash the secret using HMAC with SHA-256
def hash_secret(secret):
    return hmac.new(HMAC_SECRET_KEY.encode(), secret.encode(), hashlib.sha256).hexdigest()

# Store the hashed secret in PostgreSQL
def store_hashed_secret(eth_address, hashed_secret, ip_address):
    new_user = User(
        eth_address=eth_address,
        rtmp_secret=hashed_secret,
        ip_address=ip_address
    )
    db.session.add(new_user)
    db.session.commit()


# Retrieve the hashed secret from PostgreSQL
def get_hashed_secret(eth_address):
    user = User.query.filter_by(eth_address=eth_address).first()
    if user:
        return user.rtmp_secret
    return None

# Store a magnet URL associated with the eth_address
def store_magnet_url(eth_address, magnet_url, snapshot_index):
    new_magnet_url = MagnetURL(eth_address=eth_address, magnet_url=magnet_url, snapshot_index=snapshot_index)
    db.session.add(new_magnet_url)
    db.session.commit()
    return {"message": "Magnet URL stored successfully"}, 200

    
@app.route('/get_magnet_urls/<eth_address>', methods=['GET'])
def retrieve_magnet_urls(eth_address):
    urls = MagnetURL.query.filter_by(eth_address=eth_address).order_by(MagnetURL.snapshot_index).all()
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
        return jsonify({"message": "failure"}), 404

# API to generate and store a new secret
@app.route('/generate_secret', methods=['POST'])
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
        new_secret = generate_secret()
        logging.info(f"Generated plaintext secret: {new_secret}")

        hashed_secret = hash_secret(new_secret)
        logging.info(f"Hashed secret: {hashed_secret}")

        logging.info("Storing hashed secret in database...")
        store_hashed_secret(eth_address, hashed_secret, ip_address)
        logging.info("Successfully stored secret in DB.")

        logging.info("===== [END] /generate_secret =====")
        return jsonify({"eth_address": eth_address, "secret": new_secret}), 200

    except Exception as e:
        logging.exception(f"Unhandled exception in /generate_secret: {e}")
        return jsonify({"error": "Internal server error"}), 500


# API to retrieve the RTMP URL for a user
@app.route('/get_rtmp_url/<eth_address>', methods=['GET'])
def get_rtmp_url(eth_address):
    # Retrieve the hashed secret from PostgreSQL
    hashed_secret = get_hashed_secret(eth_address)

    if hashed_secret:
        # Construct RTMP URL with the secret
        rtmp_url = f"rtmp://psichos.is:1935/live/{eth_address}?secret={hashed_secret}"
        return jsonify({"rtmp_url": rtmp_url}), 200
    else:
        return jsonify({"error": "Secret not found"}), 404

# API to store a magnet URL
@app.route('/store_magnet_url', methods=['POST'])
def store_magnet_url_route():
    data = request.json
    eth_address = data.get('eth_address')
    magnet_url = data.get('magnet_url')
    snapshot_index = data.get('snapshot_index')

    if not eth_address or not magnet_url or snapshot_index is None:
        return jsonify({"error": "Missing required fields"}), 400

    return store_magnet_url(eth_address, magnet_url, snapshot_index)




# API to clear all magnet URLs for a specific eth_address
@app.route('/clear_magnet_urls/<eth_address>', methods=['DELETE'])
def clear_magnet_urls_route(eth_address):
    return clear_magnet_urls(eth_address)


# API to store streamer information (eth_address, hashed_secret, and IP address)
@app.route('/store_streamer_info', methods=['POST'])
def store_streamer_info():
    data = request.json
    eth_address = data.get('eth_address')
    hashed_secret = data.get('hashed_secret')
    ip_address = data.get('ip_address')

    logging.info(f"Storing streamer info: eth_address={eth_address}, hashed_secret={hashed_secret}, ip_address={ip_address}")


    if not eth_address or not hashed_secret or not ip_address:
        return jsonify({"error": "Missing required fields"}), 400


    try:
        # Store or update the streamer information in the PostgreSQL database
        user = User.query.filter_by(eth_address=eth_address).first()
        if user:
            # Update the existing record with the new hashed_secret and ip_address
            user.rtmp_secret = hashed_secret
            # Assuming you have an IP column in the database
            user.ip_address = ip_address  # You would need to add this field in the model
        else:
            # Create a new user record if it doesn't exist
            user = User(eth_address, hashed_secret)
            user.ip_address = ip_address  # Set the IP address

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Streamer info stored successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to store streamer info: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to store streamer info"}), 500

# API to get the streamer's IP address based on their Ethereum address
@app.route('/get_streamer_eth_address/<ip_address>', methods=['GET'])
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


@app.route('/verify_secret', methods=['POST'])
def verify_secret():
    eth_address = request.json.get('eth_address')
    secret = request.json.get('secret')

    if not eth_address or not secret:
        return jsonify({"error": "Missing Ethereum address or secret"}), 400

    stored_hashed_secret = get_hashed_secret(eth_address)
    if not stored_hashed_secret:
        return jsonify({"error": "Secret not found"}), 404

    hashed_secret = hash_secret(secret)

    if hmac.compare_digest(hashed_secret, stored_hashed_secret):
        return jsonify({"message": "Secret verified successfully"}), 200
    else:
        return jsonify({"error": f"Invalid secret: stored={stored_hashed_secret}, provided={secret}"}), 403


if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
