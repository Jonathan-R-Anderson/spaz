#!/bin/bash
set -e

source /app/.env

echo "🔐 Checking and copying Kerberos configuration..."
if [[ -f "/kerberos/output/krb5.conf" && -f "/kerberos/output/service.keytab" ]]; then
  cp /kerberos/output/krb5.conf /etc/krb5.conf
  cp /kerberos/output/service.keytab /etc/krb5.keytab
  echo "✅ Kerberos files copied successfully."
else
  echo "❌ Kerberos files not found in /kerberos/output. Cannot continue."
  exit 1
fi

if [ "$VPN_SETUP_MODE" == "true" ]; then
  echo "🔧 Starting configuration web UI..."
  python3 /app/config_server.py
else
  echo "🔐 Setup complete. Starting OpenVPN server..."
  openvpn --config /etc/openvpn/server.conf
fi
