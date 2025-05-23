import os
from dotenv import load_dotenv

load_dotenv()

class KerberosConfig:
    def __init__(self):
        self.REALM = os.getenv("REALM", "EXAMPLE.COM").upper()
        self.DOMAIN = os.getenv("DOMAIN", "vpn.localhost").lower()
        self.PRINCIPAL = os.getenv("PRINCIPAL", f"HTTP/{self.DOMAIN}@{self.REALM}")
        self.KEYTAB_PATH = os.getenv("KEYTAB_PATH", "/kerberos/output/service.keytab")
        self.MASTER_PASS = os.getenv("KRB5_MASTER_PASSWORD")

        self._validate()

    def _validate(self):
        if not self.MASTER_PASS:
            raise ValueError("❌ KRB5_MASTER_PASSWORD must be set in .env")