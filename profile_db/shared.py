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

# Load environment variables
load_dotenv()

# Constants from environment
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "./uploads")).resolve()
THUMB_FOLDER = Path(os.getenv("THUMB_FOLDER", UPLOAD_FOLDER / "thumbs")).resolve()
HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')
WEBTORRENT_CONTAINER_URL = os.getenv("WEBTORRENT_CONTAINER_URL", "https://webtorrent_seeder:5002")
DB_API_URL = os.getenv("DB_API_URL", "http://profile_db:5003")
BLACKLIST_FILE = os.getenv("BLACKLIST_FILE", "blacklist.json")
WHITELIST_FILE = os.getenv("WHITELIST_FILE", "whitelist.json")

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
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["THUMB_FOLDER"] = THUMB_FOLDER
app.config["SERVE_STATIC"] = True
app.config["SERVE_REST"] = True
app.config["USE_RECAPTCHA"] = False
app.config["FIREHOSE_LENGTH"] = 10

if os.getenv("MANIWANI_CFG"):
    app.config.from_envvar("MANIWANI_CFG")

app.url_map.strict_slashes = False
rest_api = Api(app)
session_store = {}
client = docker.from_env()

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

blacklist = load_json_file(BLACKLIST_FILE)
whitelist = load_json_file(WHITELIST_FILE)

def save_blacklist(data):
    save_json_file(BLACKLIST_FILE, data)

def save_whitelist(data):
    save_json_file(WHITELIST_FILE, data)

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
