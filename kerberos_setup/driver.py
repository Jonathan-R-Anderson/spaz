# driver.py
import subprocess
import os
from config import REALM, DOMAIN, PRINCIPAL, KEYTAB_PATH, MASTER_PASS

def write_krb5_conf():
    path = "/kerberos/output/krb5.conf"

    if os.path.isdir(path):
        os.rmdir(path)

    krb5_template = f"""
[libdefaults]
    default_realm = {REALM}
    dns_lookup_realm = false
    dns_lookup_kdc = false

[realms]
    {REALM} = {{
        kdc = localhost
        admin_server = localhost
    }}

[domain_realm]
    .{REALM.lower()} = {REALM}
    {REALM.lower()} = {REALM}
"""

    with open(path, "w") as f:
        f.write(krb5_template)

def initialize_kdc():
    stash_path = f"/etc/krb5kdc/.k5.{REALM}"
    db_base = "/var/lib/krb5kdc/principal"

    if not os.path.exists(stash_path):
        print(f"🛠️ Found DB but missing stash file {stash_path}, deleting DB and recreating...")
        for suffix in ["", ".ok", ".kadm5", ".kadm5.lock", ".db"]:
            path = f"{db_base}{suffix}"
            try:
                os.remove(path)
                print(f"🧹 Deleted {path}")
            except FileNotFoundError:
                continue

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
    subprocess.run(["tail", "-f", "/dev/null"])
