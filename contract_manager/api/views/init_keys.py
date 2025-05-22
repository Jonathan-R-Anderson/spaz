import os
from eth_account import Account
from system.logging import setup_logger
from config import Config

# Initialize logger
logger = setup_logger("eth_key_manager")

KEY_PATH = "/app/keys/eth_key.json"
key_dir = os.path.dirname(KEY_PATH)

# Ensure directory exists
try:
    os.makedirs(key_dir, exist_ok=True)
    logger.debug(f"[KEY_INIT] Ensured directory exists: {key_dir}")
except Exception as e:
    logger.error(f"[KEY_INIT] Failed to create directory {key_dir}: {e}")
    raise

# Generate or load key
if not os.path.exists(KEY_PATH):
    logger.info("[KEY_GEN] No existing key found. Generating new Ethereum account...")
    acct = Account.create()
    try:
        with open(KEY_PATH, "w") as f:
            f.write(acct.key.hex())
        logger.info(f"[KEY_GEN] ✅ New key generated and saved: {acct.address}")
    except Exception as e:
        logger.error(f"[KEY_GEN] ❌ Failed to save new key: {e}")
        raise
else:
    logger.info("[KEY_LOAD] Existing key file found. Loading...")
    try:
        with open(KEY_PATH, "r") as f:
            private_key = f.read().strip()
        acct = Account.from_key(private_key)
        logger.info(f"[KEY_LOAD] 🔁 Loaded existing key: {acct.address}")
    except Exception as e:
        logger.error(f"[KEY_LOAD] ❌ Failed to load existing key: {e}")
        raise
