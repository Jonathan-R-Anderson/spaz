import os

class Config:
    LOG_FILE_PATH = os.path.join("logs", "app.log")

    WEBTORRENT_URI = f"{os.getenv('WEBTORRENT_URI', 'https://webtorrent')}:{os.getenv('WEBTORRENT_PORT', 5002)}"
    DATABASE_URI = f"{os.getenv('DATABASE_URI', 'database')}:{os.getenv('DATABASE_PORT', 5003)}"
    HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')
    FILE_DIR = os.getenv('FILE_DIR', 'hosted')
    TRACKER_PORT = os.getenv('TRACKER_PORT', 5000)
    BLOCKCHAIN_URI = f"{os.getenv('BLOCKCHAIN_URI', 'https://blockchain')}:{os.getenv('BLOCKCHAIN_PORT', 5005)}"
    SECURE_MESSAGE = "Please sign this message to verify ownership of your Ethereum address."
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
