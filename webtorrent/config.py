import os
from threading import Lock

class Config:
    LOG_FILE_PATH = os.getenv("WEBTORRENT_LOG_PATH", "logs/webtorrent.log")
    HLS_DIR = os.getenv("HLS_DIR", "/app/static/hls")
    SEED_THRESHOLD = int(os.getenv("SEED_THRESHOLD", 10))
    STATIC_FOLDER = '/app/static'
    HLS_FOLDER = os.path.join(STATIC_FOLDER, 'hls')
    DATABASE_URI = f"{os.getenv('DATABASE_URI', 'http://database')}:{os.getenv('DATABASE_PORT', 5003)}"

    magnet_url_lock = Lock()
    is_monitoring_static = {}
    is_monitoring_hls = {}
    seeded_files = {}
    seed_processes = {}
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
