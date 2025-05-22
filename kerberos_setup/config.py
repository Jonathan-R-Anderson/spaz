import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

REALM = os.getenv("REALM", "EXAMPLE.COM").upper()
DOMAIN = os.getenv("DOMAIN", "vpn.localhost").lower()
PRINCIPAL = f"HTTP/{DOMAIN}@{REALM}"
KEYTAB_PATH = os.getenv("KEYTAB", "/tmp/service.keytab")
MASTER_PASS = os.getenv("KRB5_MASTER_PASSWORD")

# Write kadm5.acl
with open("/etc/krb5kdc/kadm5.acl", "w") as f:
    f.write(f"*/admin@{REALM} *\n")

# Create the DB non-interactively
subprocess.run(["kdb5_util", "create", "-s", "-P", MASTER_PASS], check=True)

# Create service principal and keytab
subprocess.run(["kadmin.local", "-q", f"addprinc -randkey {PRINCIPAL}"], check=True)
subprocess.run(["kadmin.local", "-q", f"ktadd -k {KEYTAB_PATH} {PRINCIPAL}"], check=True)