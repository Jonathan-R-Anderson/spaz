#!/bin/bash

set -e
export PYTHONPATH=/app

# Start PostgreSQL
service postgresql start

# Start Redis
service redis-server start

# Wait for PostgreSQL to be ready
until pg_isready -h localhost; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Create DB user and database if they don't exist
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='admin'\" | grep -q 1 || psql -c \\\"CREATE USER admin WITH PASSWORD 'admin';\\\""
su - postgres -c "psql -c \\\"ALTER USER admin WITH SUPERUSER;\\\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='rtmp_db'\" | grep -q 1 || psql -c \\\"CREATE DATABASE rtmp_db;\\\""
su - postgres -c "psql -c \\\"GRANT ALL PRIVILEGES ON DATABASE rtmp_db TO admin;\\\""

# Restart PostgreSQL to ensure proper auth is picked up
service postgresql restart

# Wait again for DB to be ready
until pg_isready -h localhost; do
  >&2 echo "Waiting for Postgres to restart - sleeping"
  sleep 1
done

# Start Flask app in the background (this will create tables via driver.py)
echo "Starting Flask app..."
python3 driver.py &

FLASK_PID=$!

# Wait for Flask app to become reachable
until nc -z localhost 5003; do
  >&2 echo "Waiting for Flask app to start..."
  sleep 1
done

# Run unit tests
echo "Running unit tests..."
if ! pytest tests/; then
  echo "❌ Tests failed. Shutting down Flask app and container..."
  kill $FLASK_PID
  wait $FLASK_PID
  exit 1
fi

echo "✅ All tests passed. Bringing Flask app to foreground..."
wait $FLASK_PID
