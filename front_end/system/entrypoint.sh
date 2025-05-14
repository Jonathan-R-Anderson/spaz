#!/bin/bash

set -e
cd /app
export PYTHONPATH=/app

echo "[ENTRYPOINT] Starting services..."

# Start Nginx and Mediamtx in background
nginx &
NGINX_PID=$!

/opt/mediamtx/mediamtx &
MEDIA_PID=$!

# Start supervisord to launch Flask, Gunicorn, etc.
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
SUPERVISOR_PID=$!

# Wait briefly to let services boot
echo "[ENTRYPOINT] Waiting for services to boot..."
sleep 5

# Run tests with output shown
echo "[ENTRYPOINT] Running tests..."
if pytest --maxfail=1 --disable-warnings --tb=short /app/tests/ | tee /app/logs/test_output.log; then
    echo "[ENTRYPOINT] ✅ Tests passed. Continuing with container."
else
    echo "[ENTRYPOINT] ❌ Tests failed. Output was:"
    cat /app/logs/test_output.log
    echo "[ENTRYPOINT] Shutting down services."
    kill $SUPERVISOR_PID $MEDIA_PID $NGINX_PID
    exit 1
fi

# Wait on supervisord (which manages Gunicorn)
wait $SUPERVISOR_PID
