#!/bin/bash
set -ex

echo "💥 [entrypoint] Script is running"

POSTGRES_CONF="/app/postgresql.conf"

# Wait for PostgreSQL to generate the config file
until [ -f "$POSTGRES_CONF" ]; do
  echo "[entrypoint] Waiting for $POSTGRES_CONF to exist..."
  sleep 1
done

chown postgres:postgres "$POSTGRES_CONF"

# Start Redis
service redis-server start

# Wait for PG to be ready
until pg_isready -h localhost -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

# Create tables
python3 /app/driver.py --init-db
