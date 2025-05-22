# driver.py
import subprocess
import os
from config import REALM, DOMAIN, PRINCIPAL, KEYTAB_PATH, MASTER_PASS

def write_krb5_conf():
    krb5_template = f"""[libdefaults]
  default_realm = {REALM}
  dns_lookup_realm = false
  dns_lookup_kdc = false

[realms]
  {REALM} = {{
    kdc = localhost
    admin_server = localhost
  }}

[domain_realm]
  .{DOMAIN} = {REALM}
  {DOMAIN} = {REALM}
"""
    os.makedirs("/kerberos/output", exist_ok=True)
    with open("/kerberos/output/krb5.conf", "w") as f:
        f.write(krb5_template)

    # ✅ copy into correct location now that container is running
    subprocess.run(["cp", "/kerberos/output/krb5.conf", "/etc/krb5.conf"], check=True)

def initialize_kdc():
    with open("/etc/krb5kdc/kdc.conf", "w") as f:
        f.write(f"{REALM}\n")
    with open("/etc/krb5kdc/kadm5.acl", "w") as f:
        f.write(f"*/admin@{REALM} *\n")

    print(f"🔥 Initializing KDC for realm: {REALM}")
    if not os.path.exists("/var/lib/krb5kdc/principal"):
        subprocess.run(["kdb5_util", "create", "-s", "-P", MASTER_PASS], check=True)
    else:
        print("🟡 KDC already initialized. Skipping creation.")

    subprocess.run(["kdb5_util", "create", "-s", "-P", MASTER_PASS], check=True)

def create_principal():
    print(f"🧪 Creating service principal: {PRINCIPAL}")
    subprocess.run(["kadmin.local", "-q", f"addprinc -randkey {PRINCIPAL}"], check=True)
    subprocess.run(["kadmin.local", "-q", f"ktadd -k {KEYTAB_PATH} {PRINCIPAL}"], check=True)
    print(f"✅ Keytab generated at {KEYTAB_PATH}")

if __name__ == "__main__":
    write_krb5_conf()
    initialize_kdc()
    create_principal()
    subprocess.run(["tail", "-f", "/dev/null"])  # Keep container running
