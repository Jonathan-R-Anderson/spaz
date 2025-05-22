#!/bin/bash
set -e

echo "🔐 Waiting for Kerberos files to be generated..."

# Wait up to 20 seconds for Kerberos files to be present
for i in {1..10}; do
  if [[ -f "/kerberos/output/krb5.conf" && -f "/kerberos/output/service.keytab" ]]; then
    echo "✅ Kerberos files found."
    break
  fi
  echo "⌛ Waiting for Kerberos files... ($i/10)"
  sleep 2
done

# Final check
if [[ ! -f "/kerberos/output/krb5.conf" || ! -f "/kerberos/output/service.keytab" ]]; then
  echo "❌ Kerberos files not found in /kerberos/output. Cannot continue."
  exit 1
fi

echo "📁 Copying Kerberos files to container..."

# Copy to writable location and set env var
cp /kerberos/output/krb5.conf /app/krb5.conf
cp /kerberos/output/service.keytab /etc/krb5.keytab
export KRB5_CONFIG=/app/krb5.conf

echo "✅ Kerberos configuration loaded."

if [ "$VPN_SETUP_MODE" == "true" ]; then
  echo "🔧 Starting configuration web UI..."
  python3 /app/config_server.py
else
  echo "🔐 Setup complete. Starting OpenVPN server..."
  openvpn --config /etc/openvpn/server.conf
fi
