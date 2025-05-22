# driver.py
import subprocess
import os
from config import REALM, DOMAIN, PRINCIPAL, KEYTAB_PATH, MASTER_PASS

def write_krb5_conf():
    path = "/kerberos/output/krb5.conf"
    if os.path.isdir(path):
        os.rmdir(path)  # or shutil.rmtree(path) if needed

    with open(path, "w") as f:
        f.write(f"""[libdefaults]
    default_realm = {REALM}
[realms]
    {REALM} = {{
        kdc = localhost
        admin_server = localhost
    }}
""")
    os.makedirs("/kerberos/output", exist_ok=True)
    with open("/kerberos/output/krb5.conf", "w") as f:
        f.write(krb5_template)

    # ✅ copy into correct location now that container is running
    subprocess.run(["cp", "/kerberos/output/krb5.conf", "/etc/krb5.conf"], check=True)

def initialize_kdc():
    stash_file = f"/etc/krb5kdc/.k5.{REALM}"

    print(f"🔥 Initializing KDC for realm: {REALM}")
    if os.path.exists("/var/lib/krb5kdc/principal"):
        if not os.path.exists(stash_file):
            print(f"🛠️ Found DB but missing stash file {stash_file}, deleting DB and recreating...")
            os.remove("/var/lib/krb5kdc/principal")
            if os.path.exists(stash_file):
                os.remove(stash_file)
        else:
            print("🟡 KDC already initialized. Skipping creation.")
            return

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
