#!/bin/bash

set -e

echo "[ENTRYPOINT] Starting services..."

# Start NGINX (from compiled source) and Flask via supervisord
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &
SUPERVISOR_PID=$!

echo "[ENTRYPOINT] Waiting for services to initialize..."
sleep 5

# Run tests (adjust to your testing setup — this assumes app has a test suite)
echo "[ENTRYPOINT] Running tests..."
if pytest --tb=short -v | tee /app/test_output.log; then
    echo "[ENTRYPOINT] ✅ Tests passed."
else
    echo "[ENTRYPOINT] ❌ Tests failed. Output:"
    cat /app/test_output.log
    echo "[ENTRYPOINT] Shutting down services..."
    kill $SUPERVISOR_PID
    exit 1
fi

# Wait on supervisord
wait $SUPERVISOR_PID
