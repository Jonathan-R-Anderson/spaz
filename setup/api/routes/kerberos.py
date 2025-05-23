from flask import Flask, jsonify
import subprocess
import os
from config import REALM, DOMAIN, PRINCIPAL, KEYTAB_PATH, MASTER_PASS


# --- Endpoint: Write krb5.conf ---
@app.route('/kerberos/write_conf', methods=['POST'])
def write_krb5_conf():
    path = "/kerberos/output/krb5.conf"
    if os.path.isfile(path):
        os.remove(path)

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

    os.chmod(path, 0o644)
    return jsonify({"message": "krb5.conf written", "path": path})

# --- Endpoint: Initialize KDC ---
@app.route('/kerberos/init_kdc', methods=['POST'])
def initialize_kdc():
    stash_path = f"/etc/krb5kdc/.k5.{REALM}"
    db_base = "/var/lib/krb5kdc/principal"

    if not os.path.exists(stash_path):
        deleted = []
        for suffix in ["", ".ok", ".kadm5", ".kadm5.lock", ".db"]:
            path = f"{db_base}{suffix}"
            try:
                os.remove(path)
                deleted.append(path)
            except FileNotFoundError:
                continue

        subprocess.run(["kdb5_util", "create", "-s", "-P", MASTER_PASS], check=True)
        return jsonify({"message": "KDC database created", "deleted": deleted})
    else:
        return jsonify({"message": "Stash file exists, skipping creation", "stash_path": stash_path})

# --- Endpoint: Create Principal ---
@app.route('/kerberos/create_principal', methods=['POST'])
def create_principal():
    subprocess.run(["kadmin.local", "-q", f"addprinc -randkey {PRINCIPAL}"], check=True)
    subprocess.run(["kadmin.local", "-q", f"ktadd -k {KEYTAB_PATH} {PRINCIPAL}"], check=True)
    os.chmod(KEYTAB_PATH, 0o644)

    return jsonify({"message": "Principal created and keytab generated", "keytab_path": KEYTAB_PATH})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
