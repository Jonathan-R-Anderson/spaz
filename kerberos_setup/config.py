import os
from dotenv import load_dotenv

load_dotenv()

REALM = os.getenv("REALM", "EXAMPLE.COM").upper()
DOMAIN = os.getenv("DOMAIN", "vpn.localhost").lower()
PRINCIPAL = f"HTTP/{DOMAIN}@{REALM}"
KEYTAB_PATH = os.getenv("KEYTAB", "/tmp/service.keytab")
