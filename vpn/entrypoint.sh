#!/bin/bash
set -e

echo "🔐 Waiting for Kerberos files to be generated..."

for i in {1..10}; do
  if [[ -f "/kerberos/output/krb5.conf" && -f "/kerberos/output/service.keytab" ]]; then
    echo "✅ Kerberos files found."
    break
  fi
  echo "⌛ Waiting for Kerberos files... ($i/10)"
  sleep 2
done

if [[ ! -f "/kerberos/output/krb5.conf" || ! -f "/kerberos/output/service.keytab" ]]; then
  echo "❌ Kerberos files not found in /kerberos/output. Cannot continue."
  exit 1
fi

echo "📁 Copying Kerberos files to container..."

# Use sudo if available, otherwise run as root
cp /kerberos/output/krb5.conf /tmp/krb5.conf
cp /kerberos/output/service.keytab /tmp/service.keytab
chmod 644 /tmp/krb5.conf /tmp/service.keytab

# Need root to copy to /etc
sudo cp /tmp/service.keytab /etc/krb5.keytab 2>/dev/null || cp /tmp/service.keytab /etc/krb5.keytab
export KRB5_CONFIG=/tmp/krb5.conf

echo "✅ Kerberos configuration loaded."

if [ "$VPN_SETUP_MODE" == "true" ]; then
  echo "🔧 Starting configuration web UI..."
  python3 /app/config_server.py
else
  echo "🔐 Setup complete. Starting OpenVPN server..."
  openvpn --config /etc/openvpn/server.conf
fi
