#!/bin/bash

set -e

echo "[ENTRYPOINT] Starting services..."

# Start Nginx and Mediamtx in background
nginx &
/opt/mediamtx/mediamtx &

# Start supervisord to launch Flask, etc.
supervisord -c /app/supervisord.conf

# Give services time to boot
sleep 5

echo "[ENTRYPOINT] Running tests..."
pytest --maxfail=1 --disable-warnings --tb=short tests/

if [ $? -ne 0 ]; then
    echo "[ENTRYPOINT] ❌ Tests failed. Shutting down."
    pkill supervisord
    pkill mediamtx
    pkill nginx
    exit 1
fi

echo "[ENTRYPOINT] ✅ Tests passed. Continuing with container."

# Wait on supervisord
tail -f /dev/null
