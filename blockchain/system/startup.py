# File: blockchain/system/startup.py

import os
import json
import requests
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from system.logging import setup_logger
from config import Config

CONFIG_PATH = "/app/config.json"
DEFAULT_CONTRACTS = {
    "SpazMagnetStore": {
        "abi_url": "https://gremlin.codes/abi/SpazMagnetStore.json",
        "address": "0x000..."  # Replace with actual deployed address
    }
}

console = Console()
logger = setup_logger("startup")

def display_banner():
    banner = "[bold cyan]Spaz Blockchain Configurator[/bold cyan]"
    console.print(Panel(banner, expand=False))
    logger.info("[STARTUP] Displayed startup banner")

def choose_mode():
    logger.info("[STARTUP] Prompting user for deployment mode")
    mode = inquirer.prompt([
        inquirer.List(
            'mode',
            message="Choose deployment mode",
            choices=["Federated (use existing contracts)", "Self-hosted (deploy your own)"]
        )
    ])['mode']
    logger.info(f"[STARTUP] Selected mode: {mode}")
    return mode

def fetch_remote_contracts():
    logger.info("[STARTUP] Fetching remote contract ABI definitions")
    config = {}
    for name, data in DEFAULT_CONTRACTS.items():
        try:
            logger.debug(f"[FETCH] Downloading ABI for {name} from {data['abi_url']}")
            abi = requests.get(data["abi_url"]).json()
            config[name] = {
                "address": data["address"],
                "abi": abi
            }
            logger.info(f"[FETCH] Successfully fetched ABI for {name}")
        except Exception as e:
            logger.exception(f"[FETCH] Failed to fetch ABI for {name}")
            raise
    return config

def prompt_for_custom_addresses():
    logger.info("[STARTUP] Prompting user for custom contract address and ABI path")
    try:
        address = Prompt.ask("Enter deployed SpazMagnetStore contract address")
        abi_path = Prompt.ask("Enter path to SpazMagnetStore ABI JSON")
        logger.debug(f"[PROMPT] User provided address: {address}, ABI path: {abi_path}")

        with open(abi_path) as f:
            abi = json.load(f)
        logger.info("[PROMPT] Loaded ABI from local file")
        return {
            "SpazMagnetStore": {
                "address": address,
                "abi": abi
            }
        }
    except Exception as e:
        logger.exception("[PROMPT] Failed to load ABI from file")
        raise

def write_config(config):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        console.print(f"[green]Saved config to[/green] {CONFIG_PATH}")
        logger.info(f"[CONFIG] Config successfully written to {CONFIG_PATH}")
    except Exception as e:
        logger.exception(f"[CONFIG] Failed to write config to {CONFIG_PATH}")
        raise

def main():
    try:
        display_banner()
        mode = choose_mode()

        if mode == "Federated (use existing contracts)":
            config = fetch_remote_contracts()
        else:
            config = prompt_for_custom_addresses()

        write_config(config)
        console.print("[bold green]Setup complete![/bold green]")
        logger.info("[STARTUP] Setup completed successfully")

    except Exception as e:
        console.print(f"[bold red]Setup failed:[/bold red] {e}")
        logger.critical(f"[STARTUP] Setup failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
