import os
import time
import hashlib
import logging
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import Config



# ---- LOGGING SETUP ----
log_dir = os.path.join("/app/logs")
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
        logging.debug(f"[WATCHER] Initialized with watch dir: {static_dir}")

    def on_created(self, event):
        if not event.is_directory:
            logging.debug(f"[WATCHER] File created: {event.src_path}")
            self._handle_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            logging.debug(f"[WATCHER] File modified: {event.src_path}")
            self._handle_file(event.src_path)

    def scan_existing_files(self):
        logging.info("[WATCHER] Scanning for pre-existing files...")
        for root, _, files in os.walk(self.static_dir):
            for filename in files:
                full_path = os.path.join(root, filename)
                logging.debug(f"[WATCHER] Found file: {full_path}")
                self._handle_file(full_path)

    def _handle_file(self, file_path):
        try:
            relative_path = os.path.relpath(file_path, self.static_dir)
            if not os.path.isfile(file_path):
                return

            file_hash = self._hash_file(file_path)
            logging.debug(f"[WATCHER] SHA256 for {relative_path}: {file_hash}")

            if self.hash_cache.get(relative_path) == file_hash:
                logging.debug(f"[WATCHER] No changes detected in {relative_path}")
                return

            self.hash_cache[relative_path] = file_hash
            logging.info(f"[WATCHER] Detected new/changed file: {relative_path}")

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'eth_address': Config.ETH_ADDRESS}
                logging.info(f"[WATCHER] Sending file to: {Config.WEBTORRENT_URI}/seed")
                resp = requests.post(f"{Config.WEBTORRENT_URI}/seed", files=files, data=data)

            if resp.ok:
                magnet_url = resp.json().get("magnet_url")
                logging.info(f"[WATCHER] Seeding succeeded for {relative_path} → {magnet_url}")
                self._commit_magnet_url(relative_path, magnet_url)
            else:
                logging.error(f"[WATCHER] Seeding failed for {relative_path}: {resp.status_code} {resp.text}")

        except Exception as e:
            logging.exception(f"[WATCHER] Exception while handling file {file_path}: {e}")

    def _hash_file(self, path):
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _commit_magnet_url(self, rel_path, magnet_url):
        try:
            payload = {
                "eth_address": Config.ETH_ADDRESS,
                "magnet_url": magnet_url,
                "file_path": rel_path
            }
            logging.info(f"[WATCHER] Committing magnet to blockchain...")
            resp = requests.post(f"{Config.BLOCKCHAIN_URI}/commit_magnet", json=payload)
            if resp.ok:
                logging.info(f"[WATCHER] Blockchain commit succeeded for {rel_path}")
            else:
                logging.error(f"[WATCHER] Commit failed: {resp.status_code} {resp.text}")
        except Exception as e:
            logging.exception(f"[WATCHER] Blockchain commit error for {rel_path}: {e}")

# ---- MAIN ----
def start_static_watcher():
    path = Config.FILE_DIR
    os.makedirs(path, exist_ok=True)

    logging.info(f"[WATCHER] Watching directory: {path}")
    handler = FileChangeHandler(path)
    handler.scan_existing_files()

    observer = Observer()
    observer.schedule(handler, path, recursive=True)
    observer.start()
    logging.info("[WATCHER] Observer is now running...")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logging.warning("[WATCHER] Interrupted, shutting down...")
        observer.stop()
    observer.join()
    logging.info("[WATCHER] Observer terminated.")

if __name__ == "__main__":
    start_static_watcher()
