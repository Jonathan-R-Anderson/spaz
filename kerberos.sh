#!/bin/bash

set -e

REALM="EXAMPLE.COM"
DOMAIN="vpn.localhost"
PRINCIPAL="HTTP/$DOMAIN@$REALM"
KEYTAB_DIR="./kerberos-config"
KEYTAB_FILE="$KEYTAB_DIR/service.keytab"
KRB5CONF_FILE="$KEYTAB_DIR/krb5.conf"

echo "🛠️ Installing MIT Kerberos packages..."
sudo apt update
sudo apt install -y krb5-kdc krb5-admin-server krb5-user

echo "📁 Creating Kerberos config directory: $KEYTAB_DIR"
mkdir -p "$KEYTAB_DIR"

echo "📄 Generating krb5.conf"
cat > "$KRB5CONF_FILE" <<EOF
[libdefaults]
  default_realm = $REALM
  dns_lookup_kdc = false
  dns_lookup_realm = false

[realms]
  $REALM = {
    kdc = localhost
    admin_server = localhost
  }

[domain_realm]
  .$DOMAIN = $REALM
  $DOMAIN = $REALM
EOF

echo "📦 Initializing Kerberos realm ($REALM)"
sudo krb5_newrealm

echo "🔐 Creating service principal $PRINCIPAL"
sudo kadmin.local -q "addprinc -randkey $PRINCIPAL"
sudo kadmin.local -q "ktadd -k /tmp/service.keytab $PRINCIPAL"

echo "📦 Copying keytab and krb5.conf to project directory"
sudo cp /tmp/service.keytab "$KEYTAB_FILE"
sudo chown $USER:$USER "$KEYTAB_FILE"

echo "✅ Setup complete."
echo "Your keytab and krb5.conf are in $KEYTAB_DIR"

echo "🧪 To test:"
echo "  kinit youradminuser@$REALM"
echo "  kvno $PRINCIPAL"
