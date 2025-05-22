#!/bin/bash
set -e

source /app/.env

if [ "$VPN_SETUP_MODE" == "true" ]; then
  echo "🔧 Starting configuration web UI..."
  python3 /app/config_server.py
else
  echo "🔐 Setup complete. Starting OpenVPN server..."
  openvpn --config /etc/openvpn/server.conf
fi
