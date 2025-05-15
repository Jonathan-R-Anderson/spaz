#!/bin/bash
set -ex
export PYTHONPATH=/app

# Start Redis
service redis-server start

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -U "${POSTGRES_USER:-postgres}"; do
  echo "[entrypoint] Waiting for PostgreSQL at localhost:5432..."
  sleep 1
done

# Initialize database tables
echo "[entrypoint] Creating DB tables via SQLAlchemy..."
python3 /app/driver.py --init-db

# Start Flask application
echo "[entrypoint] Starting Flask app..."
python3 /app/driver.py &
FLASK_PID=$!

# Wait for Flask to be ready
until nc -z localhost 5003; do
  echo "[entrypoint] Waiting for Flask to listen on port 5003..."
  sleep 1
done

# Run unit tests
echo "[entrypoint] Running unit tests..."
if ! pytest tests/; then
  echo "❌ Tests failed. Shutting down..."
  kill $FLASK_PID
  wait $FLASK_PID
  exit 1
fi

echo "✅ All tests passed. Bringing Flask app to foreground..."
wait $FLASK_PID
