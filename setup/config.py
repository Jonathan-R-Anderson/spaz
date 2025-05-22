# config.py
import os
from dotenv import load_dotenv

load_dotenv()

REALM = os.getenv("REALM", "EXAMPLE.COM").upper()
DOMAIN = os.getenv("DOMAIN", "vpn.localhost").lower()
PRINCIPAL = os.getenv("PRINCIPAL", f"HTTP/{DOMAIN}@{REALM}")
KEYTAB_PATH = os.getenv("KEYTAB_PATH", "/kerberos/output/service.keytab")
MASTER_PASS = os.getenv("KRB5_MASTER_PASSWORD")

if not MASTER_PASS:
    raise ValueError("❌ KRB5_MASTER_PASSWORD must be set in .env")
