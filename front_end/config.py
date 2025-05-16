import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    LOG_FILE_PATH = os.path.join("logs", "app.log")

    WEBTORRENT_URI = f"{os.getenv('WEBTORRENT_URI', 'http://webtorrent')}:{os.getenv('WEBTORRENT_PORT', 5002)}"
    BLOCKCHAIN_URI = f"{os.getenv('BLOCKCHAIN_URI', 'http://blockchain')}:{os.getenv('BLOCKCHAIN_PORT', '5005')}"
    DATABASE_URI = f"{os.getenv('DATABASE_URI', 'database')}:{os.getenv('DATABASE_PORT', 5003)}"
    HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')
    TRACKER_PORT = os.getenv('TRACKER_PORT', 5000)
    SECURE_MESSAGE = "Please sign this message to verify ownership of your Ethereum address."
    SHARED_DIR = os.getenv("SHARED_DIR", "/app")
    FILE_DIR = os.path.join(SHARED_DIR, "uploads")
    UPLOAD_DIR = os.path.join(SHARED_DIR, "uploads")
    ETH_ADDRESS = os.getenv("WATCHDOG_ETH", "0x000000000000000000000000000000000000dead")
