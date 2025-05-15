#!/bin/bash
set -ex
export PYTHONPATH=/app

# Start Redis (optional)
service redis-server start

chown -R postgres:postgres /var/lib/postgresql/data

# Start PostgreSQL in the background using official entrypoint
su - postgres -c "/usr/lib/postgresql/13/bin/postgres -D /var/lib/postgresql/data"


# Wait for PostgreSQL to come up
until pg_isready -h localhost -U "${POSTGRES_USER:-postgres}"; do
  echo "[entrypoint] Waiting for PostgreSQL at localhost:5432..."
  sleep 1
done

# Run SQLAlchemy DB init
echo "[entrypoint] Creating DB tables via SQLAlchemy..."
python3 /app/driver.py --init-db

# Start Flask app
echo "[entrypoint] Starting Flask app in background..."
python3 /app/driver.py &
FLASK_PID=$!

# Wait for Flask to be ready
until nc -z localhost 5003; do
  echo "[entrypoint] Waiting for Flask to listen on port 5003..."
  sleep 1
done

# Run tests
echo "[entrypoint] Running unit tests..."
if ! pytest tests/; then
  echo "❌ Tests failed. Shutting down Flask app..."
  kill $FLASK_PID
  wait $FLASK_PID
  exit 1
fi

echo "✅ All tests passed. Bringing Flask app to foreground..."
wait $FLASK_PID
