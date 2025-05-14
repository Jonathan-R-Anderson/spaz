#!/bin/bash

set -e

cd /app
export PYTHONPATH=$(pwd)

echo "[ENTRYPOINT] Starting services..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &
SUPERVISOR_PID=$!

echo "[ENTRYPOINT] Waiting for services to initialize..."
sleep 5

echo "[ENTRYPOINT] Verifying /app/tests exists:"
ls -l /app/tests || echo "❌ /app/tests is missing!"

echo "[ENTRYPOINT] Running tests..."
if pytest /app/tests/ --tb=short -v | tee test_output.log; then
    echo "[ENTRYPOINT] ✅ Tests passed. Continuing with container."
else
    echo "[ENTRYPOINT] ❌ Tests failed. Output:"
    cat test_output.log
    echo "[ENTRYPOINT] Shutting down services..."
    kill $SUPERVISOR_PID
    exit 1
fi

wait $SUPERVISOR_PID
