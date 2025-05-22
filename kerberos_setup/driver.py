import subprocess
from config import REALM, DOMAIN, PRINCIPAL, KEYTAB_PATH

def write_krb5_conf_template():
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
    with open("krb5.conf.template", "w") as f:
        f.write(krb5_template)
    subprocess.run(["cp", "krb5.conf.template", "/etc/krb5.conf"], check=True)

def initialize_kdc():
    with open("/etc/krb5kdc/kdc.conf", "w") as f:
        f.write(f"{REALM}\n")
    with open("/etc/krb5kdc/kadm5.acl", "w") as f:
        f.write(f"*/admin@{REALM} *\n")

    print(f"🔥 Initializing KDC for realm: {REALM}")
    subprocess.run(["krb5_newrealm"], check=True)

def create_principal():
    print(f"🧪 Creating service principal: {PRINCIPAL}")
    subprocess.run(["kadmin.local", "-q", f"addprinc -randkey {PRINCIPAL}"], check=True)
    subprocess.run(["kadmin.local", "-q", f"ktadd -k {KEYTAB_PATH} {PRINCIPAL}"], check=True)
    print(f"✅ Keytab generated at {KEYTAB_PATH}")

if __name__ == "__main__":
    write_krb5_conf_template()
    initialize_kdc()
    create_principal()
    subprocess.run(["tail", "-f", "/dev/null"])  # Keep container running
