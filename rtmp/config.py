import os

class Config:
    # Static configuration
    STREAM_DIR = "/streams"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this")
    LOG_FILE_PATH = os.getenv("RTMP_LOG_PATH", os.path.join("logs", "rtmp.log"))

    # Static/HLS directories
    STATIC_FOLDER = '/app/static'
    HLS_FOLDER = os.path.join(STATIC_FOLDER, 'hls')

    # External service URLs (can be overridden via .env)
    WEBTORRENT_CONTAINER_URL = f"{os.getenv('WEBTORRENT_CONTAINER_URL', 'https://webtorrent')}:{os.getenv('WEBTORRENT_PORT', 5002)}"
    DATABASE_URL = f"{os.getenv('DATABASE_URL', 'http://database')}:{os.getenv('DATABASE_PORT', 5003)}"
    HOSTNAME = os.getenv("HOSTNAME", "http://psichos.is")
