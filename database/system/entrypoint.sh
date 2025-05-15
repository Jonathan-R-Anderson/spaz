#!/bin/bash
set -ex
export PYTHONPATH=/app

# Start Redis
service redis-server start

# Initialize PostgreSQL if not initialized
if [ ! -s "/var/lib/postgresql/data/PG_VERSION" ]; then
  echo "[entrypoint] Initializing database..."
  su - postgres -c "/usr/lib/postgresql/13/bin/initdb -D /var/lib/postgresql/data"
fi

# Fix permissions
chown -R postgres:postgres /var/lib/postgresql/data

# Start PostgreSQL in background
su - postgres -c "/usr/lib/postgresql/13/bin/postgres -D /var/lib/postgresql/data" &
PG_PID=$!

# Wait for PostgreSQL
until pg_isready -h localhost -U "${POSTGRES_USER:-postgres}"; do
  echo "[entrypoint] Waiting for PostgreSQL at localhost:5432..."
  sleep 1
done

# Run DB initialization
echo "[entrypoint] Creating DB tables via SQLAlchemy..."
python3 /app/driver.py --init-db

# Start Flask app in background
echo "[entrypoint] Starting Flask app..."
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
  echo "❌ Tests failed. Shutting down..."
  kill $FLASK_PID
  kill $PG_PID
  wait $FLASK_PID
  wait $PG_PID
  exit 1
fi

echo "✅ All tests passed. Bringing Flask app to foreground..."
wait $FLASK_PID
