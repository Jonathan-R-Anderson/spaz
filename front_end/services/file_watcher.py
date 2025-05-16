import os
import time
import hashlib
import logging
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---- CONFIG ----
class Config:
    WEBTORRENT_URI = f"{os.getenv('WEBTORRENT_URI', 'http://webtorrent')}:{os.getenv('WEBTORRENT_PORT', '5002')}"
    BLOCKCHAIN_URI = f"{os.getenv('BLOCKCHAIN_URI', 'http://blockchain')}:{os.getenv('BLOCKCHAIN_PORT', '5005')}"
    FILE_DIR = "/app/static"  # Directory to watch

# ---- LOGGING SETUP ----
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "file_watcher.log")),
        logging.StreamHandler()
    ]
)

# ---- FILE WATCHER ----
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, static_dir):
        self.static_dir = static_dir
        self.hash_cache = {}
        logging.debug(f"[WATCHER] Initialized FileChangeHandler with directory: {static_dir}")

    def on_created(self, event):
        if not event.is_directory:
            logging.debug(f"[WATCHER] File created: {event.src_path}")
            self._handle_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            logging.debug(f"[WATCHER] File modified: {event.src_path}")
            self._handle_file(event.src_path)

    def scan_existing_files(self):
        logging.info("[WATCHER] Scanning existing files on startup...")
        for root, _, files in os.walk(self.static_dir):
            for filename in files:
                full_path = os.path.join(root, filename)
                logging.debug(f"[WATCHER] Found existing file: {full_path}")
                self._handle_file(full_path)

    def _handle_file(self, file_path):
        logging.info(f"[WATCHER] Detected change in: {file_path}")
        try:
            file_hash = self._hash_file(file_path)
            relative_path = os.path.relpath(file_path, self.static_dir)

            logging.debug(f"[WATCHER] Computed SHA256 hash: {file_hash} for file: {relative_path}")

            if self.hash_cache.get(relative_path) == file_hash:
                logging.debug(f"[WATCHER] No change in file contents for: {relative_path}")
                return

            self.hash_cache[relative_path] = file_hash
            logging.debug(f"[WATCHER] Updated hash cache for: {relative_path}")

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'eth_address': '0xSTATIC_MONITOR'}
                logging.info(f"[WATCHER] Sending file to seed endpoint: {Config.WEBTORRENT_URI}/seed")
                resp = requests.post(f"{Config.WEBTORRENT_URI}/seed", files=files, data=data)

            if resp.ok:
                logging.info(f"[WATCHER] Seed successful for file: {relative_path}")
                magnet_url = resp.json().get("magnet_url")
                logging.debug(f"[WATCHER] Received magnet URL: {magnet_url}")
                commit_payload = {
                    "eth_address": "0xSTATIC_MONITOR",
                    "magnet_url": magnet_url,
                    "file_path": relative_path
                }
                logging.info(f"[WATCHER] Committing magnet URL to blockchain: {Config.BLOCKCHAIN_URI}/commit_magnet")
                chain_resp = requests.post(f"{Config.BLOCKCHAIN_URI}/commit_magnet", json=commit_payload)

                if chain_resp.ok:
                    logging.info(f"[WATCHER] Successfully committed magnet URL for file: {relative_path}")
                else:
                    logging.error(f"[WATCHER] Failed to commit magnet URL: {chain_resp.status_code}, body: {chain_resp.text}")
            else:
                logging.error(f"[WATCHER] Failed to seed file: {file_path}, status={resp.status_code}, body={resp.text}")

        except Exception as e:
            logging.exception(f"[WATCHER] Error handling file {file_path}: {e}")

    def _hash_file(self, path):
        logging.debug(f"[WATCHER] Hashing file: {path}")
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

# ---- MAIN ----
def start_static_watcher():
    path = Config.FILE_DIR
    if not os.path.exists(path):
        logging.warning(f"[WATCHER] Directory '{path}' not found. Creating it...")
        os.makedirs(path)

    logging.info(f"[WATCHER] Starting file watcher on: {path}")
    event_handler = FileChangeHandler(path)
    
    # Scan pre-existing files
    event_handler.scan_existing_files()

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logging.info("[WATCHER] Observer started and monitoring filesystem events.")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logging.warning("[WATCHER] File watcher interrupted by user.")
        observer.stop()
    observer.join()
    logging.info("[WATCHER] Observer shutdown complete.")


# ---- EXECUTE ----
if __name__ == "__main__":
    start_static_watcher()
