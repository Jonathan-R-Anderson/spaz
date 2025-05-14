import requests

CONTRACTS_BASE_URL = "http://blockchain:5005"

def get_contract_abi(contract_name: str) -> list:
    """
    Fetch the ABI of the specified contract.
    """
    endpoint = f"{CONTRACTS_BASE_URL}/{contract_name}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json().get("abi", [])
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch ABI for {contract_name}: {e}")
        return []

def get_contract_address(contract_name: str) -> str:
    """
    Fetch the contract address of the specified contract.
    """
    endpoint = f"{CONTRACTS_BASE_URL}/{contract_name}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json().get("address", "0x0")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch address for {contract_name}: {e}")
        return "0x0"

# Aliases for common contracts
def get_spaz_livestream_abi():
    return get_contract_abi("spaz_livestream")

def get_spaz_livestream_address():
    return get_contract_address("spaz_livestream")

def get_spaz_moderation_abi():
    return get_contract_abi("spaz_moderation")

def get_spaz_moderation_address():
    return get_contract_address("spaz_moderation")
