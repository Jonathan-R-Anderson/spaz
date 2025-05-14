import os

class Config:
    LOG_FILE_PATH = os.path.join("logs", "app.log")

    WEBTORRENT_CONTAINER_URL = f"{os.getenv('WEBTORRENT_CONTAINER_URL', 'https://webtorrent')}:{os.getenv('WEBTORRENT_PORT', 5002)}"
    DATABASE_URL = f"{os.getenv('DATABASE_URI', 'database')}:{os.getenv('DATABASE_PORT', 5003)}"
    HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')
    FILE_DIR = os.getenv('FILE_DIR', 'hosted')
    TRACKER_PORT = os.getenv('TRACKER_PORT', 5000)

    SECURE_MESSAGE = "Please sign this message to verify ownership of your Ethereum address."
