# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    LOG_FILE_PATH = os.getenv("DATABASE_LOG_PATH", "logs/database.log")
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://admin:admin@localhost/rtmp_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')
    WEBTORRENT_URI = os.getenv('WEBTORRENT_URI', 'https://webtorrent')
    WEBTORRENT_PORT = int(os.getenv('WEBTORRENT_PORT', 5002))
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    SHARED_DIR = os.getenv("SHARED_DIR", "/shared")
    FILE_DIR = os.path.join(SHARED_DIR, "files")
    UPLOAD_DIR = os.path.join(SHARED_DIR, "uploads")
