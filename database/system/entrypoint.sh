#!/bin/bash
set -ex

echo "💥 [entrypoint] Script is running"

POSTGRES_CONF="/app/postgresql.conf"

# Wait for PostgreSQL to generate the config file
until [ -f "$POSTGRES_CONF" ]; do
  echo "[entrypoint] Waiting for $POSTGRES_CONF to exist..."
  sleep 1
done


# Start Redis
service redis-server start

# Wait for PG to be ready
until psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -h localhost -c '\q' 2>/dev/null; do
  echo "Waiting for PostgreSQL to accept connections..."
  sleep 1
done


# Create tables
python3 /app/driver.py --init-db
