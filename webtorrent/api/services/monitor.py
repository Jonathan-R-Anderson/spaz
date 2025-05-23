import os
import logging
import subprocess
import time
from multiprocessing import Process
from threading import Lock
import requests
from threading import Thread
import re
from urllib.parse import unquote
from flask import Blueprint, render_template, request, jsonify, send_from_directory
from config import Config

def start_monitoring(eth_address):
    # Placeholder logic, or call both monitoring functions
    from multiprocessing import Process
    p1 = Process(target=monitor_static_directory, args=(eth_address,))
    p2 = Process(target=monitor_hls_directory, args=(eth_address,))
    p1.start()
    p2.start()


# Function to store a magnet URL using the DATABASE_URL API
def store_magnet_url(eth_address, magnet_url, snapshot_index):
    logging.debug(f"Storing magnet URL for {eth_address}, snapshot {snapshot_index}")
    url = f"{Config.DATABASE_URI}/store_magnet_url"
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

# Function to retrieve magnet URLs from DATABASE_URL
def retrieve_magnet_urls(eth_address):
    logging.debug(f"Retrieving magnet URLs for {eth_address}")
    url = f"{Config.DATABASE_URI}/get_magnet_urls/{eth_address}"
    
    try:
        logging.info(f"Sending GET request to retrieve magnet URLs for {eth_address}")
        response = requests.get(url)
        return response.json()
    except Exception as e:
        logging.error(f"Error calling DATABASE_URL API to retrieve magnet URLs: {e}")
        return None

def stream_output(process, eth_address, snapshot_number):
    logging.debug(f"[stream_output] Started for {eth_address}, snapshot {snapshot_number}")
    magnet_url = None

    while True:
        output = process.stdout.readline()
        if output == '':
            output = process.stderr.readline()
        if output == '' and process.poll() is not None:
            logging.debug(f"[stream_output] No more output; process ended for {eth_address}")
            break
        if output:
            logging.info(f"[stream_output] Raw line: {output.strip()}")
            if 'Magnet:' in output:
                magnet_url = output.split("Magnet: ")[1].strip()
                logging.info(f"[stream_output] Found magnet URL: {magnet_url}")
                store_magnet_url(eth_address, magnet_url, snapshot_number)
                break

    logging.debug(f"[stream_output] Completed for {eth_address}: {magnet_url}")
    return magnet_url


def monitor_static_directory(eth_address):
    if Config.is_monitoring_static.get(eth_address):
        logging.info(f"[monitor_static_directory] Already monitoring for {eth_address}")
        return
    Config.is_monitoring_static[eth_address] = True
    logging.info(f"[monitor_static_directory] Starting monitor for {eth_address}")

    latest_file = None

    while True:
        try:
            logging.debug(f"[monitor_static_directory] Scanning static folder for {eth_address}")
            static_files = sorted(
                [f for f in os.listdir(Config.STATIC_FOLDER)
                 if f.startswith(eth_address) and f.endswith('.mp4')],
                key=lambda f: os.path.getmtime(os.path.join(Config.STATIC_FOLDER, f))
            )

            if static_files and static_files[-1] != latest_file:
                latest_file = static_files[-1]
                file_path = os.path.join(Config.STATIC_FOLDER, latest_file)
                snapshot_number = extract_snapshot_number(latest_file)

                logging.info(f"[monitor_static_directory] Detected new file: {file_path}")

                process = subprocess.Popen(
                    ['/usr/bin/webtorrent', 'seed', file_path, '--announce=wss://tracker.openwebtorrent.com', '--keep-seeding'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                magnet_url = stream_output(process, eth_address, snapshot_number)

                if magnet_url:
                    logging.info(f"[monitor_static_directory] File {file_path} seeded with magnet: {magnet_url}")
                    while True:
                        try:
                            response = requests.post(
                                "http://localhost:5002/peer_count",
                                json={"magnet_url": magnet_url}
                            )
                            if response.status_code == 200:
                                peer_count = response.json().get("peer_count", 0)
                                logging.info(f"[monitor_static_directory] {magnet_url} has {peer_count} peers")

                                if peer_count > 10:
                                    logging.info(f"[monitor_static_directory] Peer count exceeded. Stopping seeding.")
                                    requests.post(
                                        "http://localhost:5002/stop_seeding",
                                        json={"eth_address": eth_address}
                                    )
                                    break
                        except Exception as e:
                            logging.error(f"[monitor_static_directory] Peer check failed: {e}")
                        time.sleep(10)
                else:
                    logging.error(f"[monitor_static_directory] Failed to generate magnet for {file_path}")

            time.sleep(5)

        except Exception as e:
            logging.error(f"[monitor_static_directory] Error: {e}")
            break

def monitor_hls_directory(eth_address):
    if Config.is_monitoring_hls.get(eth_address):
        logging.info(f"[monitor_hls_directory] Already monitoring HLS for {eth_address}")
        return
    Config.is_monitoring_hls[eth_address] = True
    logging.info(f"[monitor_hls_directory] Starting HLS monitor for {eth_address}")

    latest_file = None

    while True:
        try:
            logging.debug(f"[monitor_hls_directory] Scanning HLS folder for {eth_address}")
            mp4_files = sorted(
                [f for f in os.listdir(Config.HLS_FOLDER)
                 if f.startswith(eth_address) and f.endswith('.mp4')],
                key=lambda f: os.path.getmtime(os.path.join(Config.HLS_FOLDER, f))
            )

            if mp4_files and mp4_files[-1] != latest_file:
                latest_file = mp4_files[-1]
                file_path = os.path.join(Config.HLS_FOLDER, latest_file)
                snapshot_number = extract_snapshot_number(latest_file)

                logging.info(f"[monitor_hls_directory] Detected new snapshot file: {file_path}")

                process = subprocess.Popen(
                    ['/usr/bin/webtorrent', 'seed', file_path,
                     '--announce=wss://tracker.openwebtorrent.com',
                     '--keep-seeding'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                magnet_url = stream_output(process, eth_address, snapshot_number)

                if magnet_url:
                    logging.info(f"[monitor_hls_directory] File {file_path} seeded with magnet: {magnet_url}")
                    while True:
                        try:
                            response = requests.post(
                                "http://localhost:5002/peer_count",
                                json={"magnet_url": magnet_url}
                            )
                            if response.status_code == 200:
                                peer_count = response.json().get("peer_count", 0)
                                logging.info(f"[monitor_hls_directory] {magnet_url} has {peer_count} peers")

                                if peer_count > 10:
                                    logging.info(f"[monitor_hls_directory] Peer threshold exceeded, stopping seeding.")
                                    requests.post(
                                        "http://localhost:5002/stop_seeding",
                                        json={"eth_address": eth_address}
                                    )
                                    break
                        except Exception as e:
                            logging.error(f"[monitor_hls_directory] Peer count check failed: {e}")
                        time.sleep(10)
                else:
                    logging.error(f"[monitor_hls_directory] Failed to seed {file_path}")

            time.sleep(5)

        except Exception as e:
            logging.error(f"[monitor_hls_directory] Error: {e}")
            break


def extract_snapshot_number(filename):
    try:
        parts = filename.split('_snapshot_')
        return int(parts[1].split('.')[0])
    except Exception:
        return 0
