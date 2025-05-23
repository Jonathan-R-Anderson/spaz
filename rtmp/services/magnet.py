import os
import logging
from threading import Lock
import subprocess
import time
from multiprocessing import Process
from flask import Flask, request, jsonify
import requests
import hmac
from config import Config
from services.state import seeded_files, snapshot_indices


def seed_all_static_files_for_user(eth_address):
    logging.info(f"[seed_all_static_files_for_user] Starting seeding process for {eth_address}")
    snapshot_indices.setdefault(eth_address, 0)

    while True:
        try:
            logging.debug(f"[{eth_address}] Scanning HLS_FOLDER: {Config.HLS_FOLDER} for .m3u8 files")
            m3u8_files = sorted(
                [f for f in os.listdir(Config.HLS_FOLDER) if f.startswith(eth_address) and f.endswith('.m3u8')],
                key=lambda f: os.path.getmtime(os.path.join(Config.HLS_FOLDER, f))
            )

            for m3u8_file in m3u8_files:
                snapshot_indices[eth_address] += 1
                index = snapshot_indices[eth_address]

                logging.info(f"[{eth_address}] Submitting conversion for {m3u8_file}, snapshot {index}")
                try:
                    response = requests.post(
                        f"{Config.WEBTORRENT_CONTAINER_URL}/convert_to_mp4",
                        json={
                            "eth_address": eth_address,
                            "snapshot_index": index,
                            "filename": m3u8_file
                        },
                        timeout=60  # You may adjust timeout based on expected duration
                    )
                except Exception as e:
                    logging.error(f"[{eth_address}] ❌ Error calling convert_to_mp4: {e}")
                    continue

                if response.status_code != 200:
                    logging.error(f"[{eth_address}] Conversion failed: {response.text}")
                    continue

                resp_data = response.json()
                magnet_url = resp_data.get("magnet_url")
                output_path = resp_data.get("output_path")

                if magnet_url and output_path:
                    seeded_files[output_path] = magnet_url
                    logging.info(f"[{eth_address}] ✅ Seeded {output_path} with magnet: {magnet_url}")
                else:
                    logging.warning(f"[{eth_address}] No magnet_url returned for snapshot {index}")
                    continue

                # Monitor peer count
                logging.debug(f"[{eth_address}] Monitoring peers for magnet: {magnet_url}")
                try:
                    while True:
                        peer_resp = requests.post(f"{Config.WEBTORRENT_CONTAINER_URL}/peer_count", json={"magnet_url": magnet_url})
                        if peer_resp.status_code != 200:
                            logging.warning(f"[{eth_address}] Peer count check failed: {peer_resp.text}")
                            break
                        peer_count = peer_resp.json().get("peer_count", 0)
                        logging.info(f"[{eth_address}] Peer count: {peer_count}")
                        if peer_count > 10:
                            logging.info(f"[{eth_address}] Peer threshold reached. Stopping seeding.")
                            requests.post(f"{Config.WEBTORRENT_CONTAINER_URL}/stop_seeding", json={"eth_address": eth_address})
                            break
                        time.sleep(10)
                except Exception as e:
                    logging.error(f"[{eth_address}] Error during peer monitoring: {e}")

            logging.debug(f"[{eth_address}] Sleeping 30s before next .m3u8 scan")
            time.sleep(30)

        except Exception as e:
            logging.error(f"[seed_all_static_files_for_user] 🔥 Loop error for {eth_address}: {e}")
            break


# Function to retrieve magnet URLs from DATABASE_URL
def retrieve_magnet_urls(eth_address):
    logging.debug(f"Retrieving magnet URLs for {eth_address}")
    url = f"{Config.DATABASE_URL}/get_magnet_urls/{eth_address}"
    
    try:
        logging.info(f"Sending GET request to retrieve magnet URLs for {eth_address}")
        response = requests.get(url)
        return response.json()
    except Exception as e:
        logging.error(f"Error calling DATABASE_URL API to retrieve magnet URLs: {e}")
        return None
    

# Function to store a magnet URL using the DATABASE_URL API
def store_magnet_url(eth_address, magnet_url, snapshot_index):
    logging.debug(f"Storing magnet URL for {eth_address}, snapshot {snapshot_index}")
    url = f"{Config.HOSTNAME}/store_magnet_url"
    payload = {
        "eth_address": eth_address,
        "magnet_url": magnet_url,
        "snapshot_index": snapshot_index
    }
    
    try:
        logging.info(f"Sending POST request to store magnet URL for {eth_address}, snapshot {snapshot_index}")
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logging.info(f"Successfully stored magnet URL for {eth_address}, snapshot {snapshot_index}")
        else:
            logging.error(f"Failed to store magnet URL: {response.json()}")
    except Exception as e:
        logging.error(f"Error calling DATABASE_URL API to store magnet URL: {e}")



# Function to stream and log output from the subprocess and store the magnet URL in the database
def stream_output(process, eth_address, snapshot_number):
    logging.debug(f"Started streaming output from subprocess for {eth_address}, snapshot {snapshot_number}")
    magnet_url = None
    
    while True:
        logging.debug("Reading output from subprocess")
        output = process.stdout.readline()  # Read line from stdout
        if output == '' and process.poll() is not None:
            logging.debug(f"No more output from subprocess for {eth_address}, snapshot {snapshot_number}, process may have finished.")
            break
        if output:
            logging.info(f"Subprocess output: {output.strip()}")
            if 'Magnet:' in output:
                magnet_url = output.split("Magnet: ")[1].strip()
                logging.info(f"Magnet URL found: {magnet_url}")
                
                # Store the magnet URL in the database by calling the DATABASE_URL API
                logging.info(f"Storing magnet URL {magnet_url} for {eth_address}, snapshot {snapshot_number}")
                store_magnet_url(eth_address, magnet_url, snapshot_number)
                break
    logging.debug(f"Magnet URL streaming complete for {eth_address}, snapshot {snapshot_number}: {magnet_url}")
    return magnet_url

def get_peer_count(magnet_url):
    try:
        response = requests.post(f"{Config.WEBTORRENT_CONTAINER_URL}/peer_count", json={"magnet_url": magnet_url}, timeout=10)
        if response.status_code == 200:
            return response.json().get("peer_count", 0)
        else:
            logging.error(f"Error from peer_count endpoint: {response.text}")
    except Exception as e:
        logging.error(f"Exception while contacting webtorrent: {e}")
    return 0
