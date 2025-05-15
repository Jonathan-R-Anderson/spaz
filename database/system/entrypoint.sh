#!/bin/bash

set -e
export PYTHONPATH=/app

# Start PostgreSQL and Redis
service postgresql start
service redis-server start

# Wait for PostgreSQL to be ready
until pg_isready -h localhost; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Create DB user and database
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='admin'\" | grep -q 1 || psql -c 'CREATE USER admin WITH PASSWORD '\''admin'\'';'"
su - postgres -c "psql -c 'ALTER USER admin WITH SUPERUSER;'"
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='rtmp_db'\" | grep -q 1 || psql -c 'CREATE DATABASE rtmp_db;'"
su - postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE rtmp_db TO admin;'"

# Restart PostgreSQL again and wait
service postgresql restart
until pg_isready -h localhost; do
  echo "Waiting for Postgres to restart - sleeping"
  sleep 1
done

# Launch Flask app in background
echo "Starting Flask app for testing..."
python3 driver.py &

FLASK_PID=$!

# Wait for Flask to become available
until nc -z localhost 5003; do
  echo "Waiting for Flask app to start on port 5003..."
  sleep 1
done

# Run unit tests
echo "Running unit tests..."
if ! pytest tests/; then
  echo "❌ Tests failed. Shutting down Flask app..."
  kill $FLASK_PID
  wait $FLASK_PID
  exit 1
fi

echo "✅ All tests passed. Bringing Flask app to foreground..."
wait $FLASK_PID
