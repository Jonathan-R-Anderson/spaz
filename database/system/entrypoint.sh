#!/bin/bash

set -ex
export PYTHONPATH=/app

# Start PostgreSQL and Redis services
service postgresql start
service redis-server start

# Wait for PostgreSQL to be ready
until pg_isready -h localhost; do
  echo "[entrypoint] Waiting for PostgreSQL..."
  sleep 1
done

# Create DB user and database if they don't exist
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='admin'\" | grep -q 1 || psql -c 'CREATE USER admin WITH PASSWORD '\''admin'\'';'"
su - postgres -c "psql -c 'ALTER USER admin WITH SUPERUSER;'"
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='rtmp_db'\" | grep -q 1 || psql -c 'CREATE DATABASE rtmp_db;'"
su - postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE rtmp_db TO admin;'"

# Restart PostgreSQL to apply changes
service postgresql restart
until pg_isready -h localhost; do
  echo "[entrypoint] Waiting for PostgreSQL restart..."
  sleep 1
done


PGPASSWORD=admin psql -U admin -d rtmp_db -h localhost -c "
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    eth_address VARCHAR(42) UNIQUE NOT NULL,
    rtmp_secret VARCHAR(64) NOT NULL,
    ip_address VARCHAR(45) NOT NULL
);"

PGPASSWORD=admin psql -U admin -d rtmp_db -h localhost -c "
CREATE TABLE IF NOT EXISTS magnet_url (
    id SERIAL PRIMARY KEY,
    eth_address VARCHAR(42) NOT NULL,
    magnet_url TEXT NOT NULL,
    snapshot_index INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);"

echo "[entrypoint] Verifying tables exist..."
PGPASSWORD=admin psql -U admin -d rtmp_db -h localhost -c '\dt'

# Create tables using SQLAlchemy (inside Python app)
echo "[entrypoint] Creating DB tables via SQLAlchemy..."
PGPASSWORD=admin python3 /app/driver.py --init-db

# Start Flask app in background
echo "[entrypoint] Starting Flask app in background..."
python3 /app/driver.py &
FLASK_PID=$!

# Wait for Flask app to be reachable
until nc -z localhost 5003; do
  echo "[entrypoint] Waiting for Flask to listen on port 5003..."
  sleep 1
done

# Run unit tests
echo "[entrypoint] Running unit tests..."
if ! pytest tests/; then
  echo "❌ Tests failed. Shutting down Flask app..."
  kill $FLASK_PID
  wait $FLASK_PID
  exit 1
fi

echo "✅ All tests passed. Bringing Flask app to foreground..."
wait $FLASK_PID
