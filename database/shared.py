import os
import random
import ipaddress
from pathlib import Path
from flask import Flask
from flask_restful import Api
from werkzeug.datastructures import ImmutableDict
from web3 import Web3
import json
import logging
import docker
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from dotenv import load_dotenv
import base64
import os
import redis
import random
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

# Constants from environment
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')
WEBTORRENT_CONTAINER_URL = f"{os.getenv('WEBTORRENT_CONTAINER_URL', 'https://webtorrent_seeder')}:{os.getenv('WEBTORRENT_SEEDER_PORT', 5002)}"
DATABASE_URL = f"{os.getenv('DATABASE_URL', 'http://database')}:{os.getenv('DATABASE_PORT', 5003)}"


# Contract addresses
gremlinThreadAddress = os.getenv("GREMLIN_THREAD_ADDRESS")
gremlinReplyAddress = os.getenv("GREMLIN_REPLY_ADDRESS")
gremlinLeaderboardAddress = os.getenv("GREMLIN_LEADERBOARD_ADDRESS")
gremlinDAOAddress = os.getenv("GREMLIN_DAO_ADDRESS")
gremlinProfileAddress = os.getenv("GREMLIN_PROFILE_ADDRESS")
gremlinAdminAddress = os.getenv("GREMLIN_ADMIN_ADDRESS")
gremlinChallengeAddress = os.getenv("GREMLIN_CHALLENGE_ADDRESS")
gremlinJournalAddress = os.getenv("GREMLIN_JOURNAL_ADDRESS")

# Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)



# Flask App Initialization
class ManiwaniApp(Flask):
    jinja_options = ImmutableDict()

app = ManiwaniApp(__name__, static_url_path='')
app.config["SERVE_STATIC"] = True
app.config["SERVE_REST"] = True

app.url_map.strict_slashes = False
rest_api = Api(app)
session_store = {}
client = docker.from_env()


# Redis client to store secrets (NoSQL key-value store)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost/DATABASE_URL'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eth_address = db.Column(db.String(42), unique=True, nullable=False)
    rtmp_secret = db.Column(db.String(64), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # Ensure this field is added

    def __init__(self, eth_address, rtmp_secret):
        self.eth_address = eth_address
        self.rtmp_secret = rtmp_secret

# Define a model for storing magnet URLs
class MagnetURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eth_address = db.Column(db.String(42), nullable=False)
    magnet_url = db.Column(db.Text, nullable=False)
    snapshot_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())



# Helper functions
def load_json_file(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_json_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)


def gen_poster_id():
    return '%04X' % random.randint(0, 0xffff)

def ip_to_int(ip_str):
    return int.from_bytes(ipaddress.ip_address(ip_str).packed, byteorder="little") << 8

def allowed_file(filename):
    return True

def generate_ecc_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

# Note: elliptic curve encryption below is illustrative, real ECIES isn't this straightforward
def encrypt_secret(secret, public_key):
    return base64.b64encode(secret.encode()).decode('utf-8')
