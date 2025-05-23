import os
import subprocess
from config import Config

def write_conf():
    path = "/kerberos/output/krb5.conf"
    if os.path.isfile(path):
        os.remove(path)

    content = f"""
[libdefaults]
    default_realm = {Config.REALM}
    dns_lookup_realm = false
    dns_lookup_kdc = false

[realms]
    {Config.REALM} = {{
        kdc = localhost
        admin_server = localhost
    }}

[domain_realm]
    .{Config.REALM.lower()} = {Config.REALM}
    {Config.REALM.lower()} = {Config.REALM}
"""
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, 0o644)
    return {"message": "krb5.conf written", "path": path}


def init_kdc():
    stash_path = f"/etc/krb5kdc/.k5.{Config.REALM}"
    db_base = "/var/lib/krb5kdc/principal"
    deleted = []

    if not os.path.exists(stash_path):
        for suffix in ["", ".ok", ".kadm5", ".kadm5.lock", ".db"]:
            try:
                path = f"{db_base}{suffix}"
                os.remove(path)
                deleted.append(path)
            except FileNotFoundError:
                continue
        subprocess.run(["kdb5_util", "create", "-s", "-P", Config.MASTER_PASS], check=True)
        return {"message": "KDC database created", "deleted": deleted}
    return {"message": "Stash file exists, skipping creation", "stash_path": stash_path}


def create_principal():
    subprocess.run(["kadmin.local", "-q", f"addprinc -randkey {Config.PRINCIPAL}"], check=True)
    subprocess.run(["kadmin.local", "-q", f"ktadd -k {Config.KEYTAB_PATH} {Config.PRINCIPAL}"], check=True)
    os.chmod(Config.KEYTAB_PATH, 0o644)
    return {"message": "Principal created", "keytab_path": Config.KEYTAB_PATH}
