#!/bin/bash
set -ex
export PYTHONPATH=/app

# Start PostgreSQL in background
/docker-entrypoint.sh postgres &

# Wait until it starts
until pg_isready -h localhost -U "$POSTGRES_USER"; do
  echo "[entrypoint] Waiting for PostgreSQL at localhost:5432..."
  sleep 1
done

# Optional: Start Redis (if needed in same container)
service redis-server start

# Initialize tables
python3 /app/driver.py --init-db

# Launch Flask app
python3 /app/driver.py
