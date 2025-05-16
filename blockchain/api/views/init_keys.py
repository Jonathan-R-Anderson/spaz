import os
from eth_account import Account

KEY_PATH = "/app/keys/eth_key.json"
os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)

if not os.path.exists(KEY_PATH):
    acct = Account.create()
    with open(KEY_PATH, "w") as f:
        f.write(acct.key.hex())
    print(f"✅ New key generated: {acct.address}")
else:
    with open(KEY_PATH, "r") as f:
        private_key = f.read().strip()
    acct = Account.from_key(private_key)
    print(f"🔁 Loaded existing key: {acct.address}")
