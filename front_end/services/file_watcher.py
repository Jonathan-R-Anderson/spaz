import os
import time
import hashlib
import logging
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import Config

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, static_dir):
        self.static_dir = static_dir
        self.hash_cache = {}

    def on_created(self, event):
        if not event.is_directory:
            self._handle_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file(event.src_path)

    def _handle_file(self, file_path):
        logging.info(f"[WATCHER] Detected change in: {file_path}")
        try:
            file_hash = self._hash_file(file_path)
            relative_path = os.path.relpath(file_path, self.static_dir)

            if self.hash_cache.get(relative_path) == file_hash:
                return  # No actual change
            self.hash_cache[relative_path] = file_hash

            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'eth_address': '0xSTATIC_MONITOR'}  # or dynamic
                resp = requests.post(f"http://localhost:5002/seed", files=files, data=data)

            if resp.ok:
                magnet_url = resp.json().get("magnet_url")
                logging.info(f"[WATCHER] Magnet URL: {magnet_url}")
                requests.post(f"http://blockchain:5005/commit_magnet", json={
                    "eth_address": "0xSTATIC_MONITOR",
                    "magnet_url": magnet_url,
                    "file_path": relative_path
                })
            else:
                logging.error(f"[WATCHER] Failed to seed file: {file_path}, status={resp.status_code}")

        except Exception as e:
            logging.exception(f"[WATCHER] Error handling file {file_path}: {e}")

    def _hash_file(self, path):
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

def start_static_watcher():
    path = Config.HLS_DIR  # or Config.STATIC_DIR if defined separately
    logging.info(f"[WATCHER] Starting file watcher on {path}")
    event_handler = FileChangeHandler(path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
