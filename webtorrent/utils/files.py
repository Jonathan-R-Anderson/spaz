def is_valid_eth_address(address):
    return isinstance(address, str) and address.startswith("0x") and len(address) == 42
