# File: blockchain/system/startup.py

import os
import json
import requests
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

CONFIG_PATH = "/app/config.json"
DEFAULT_CONTRACTS = {
    "SpazMagnetStore": {
        "abi_url": "https://gremlin.codes/abi/SpazMagnetStore.json",
        "address": "0x000..."  # Replace with actual deployed address
    }
}

console = Console()

def display_banner():
    console.print(Panel("[bold cyan]Spaz Blockchain Configurator[/bold cyan]", expand=False))

def choose_mode():
    return inquirer.prompt([
        inquirer.List(
            'mode',
            message="Choose deployment mode",
            choices=["Federated (use existing contracts)", "Self-hosted (deploy your own)"]
        )
    ])['mode']

def fetch_remote_contracts():
    config = {}
    for name, data in DEFAULT_CONTRACTS.items():
        abi = requests.get(data["abi_url"]).json()
        config[name] = {
            "address": data["address"],
            "abi": abi
        }
    return config

def prompt_for_custom_addresses():
    address = Prompt.ask("Enter deployed SpazMagnetStore contract address")
    abi_path = Prompt.ask("Enter path to SpazMagnetStore ABI JSON")
    with open(abi_path) as f:
        abi = json.load(f)
    return {
        "SpazMagnetStore": {
            "address": address,
            "abi": abi
        }
    }

def write_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    console.print(f"[green]Saved config to[/green] {CONFIG_PATH}")

def main():
    display_banner()
    mode = choose_mode()

    if mode == "Federated (use existing contracts)":
        config = fetch_remote_contracts()
    else:
        config = prompt_for_custom_addresses()

    write_config(config)
    console.print("[bold green]Setup complete![/bold green]")

if __name__ == "__main__":
    main()
