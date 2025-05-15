#!/bin/bash
set -ex

chown -R postgres:postgres /var/lib/postgresql

# If config is missing, copy default
if [ ! -f /var/lib/postgresql/data/postgresql.conf ]; then
  cp /tmp/postgresql.conf /var/lib/postgresql/data/postgresql.conf
  chown postgres:postgres /var/lib/postgresql/data/postgresql.conf
fi

# Start Redis
service redis-server start

# Wait for PG to be ready
until pg_isready -h localhost -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

# Create tables
python3 /app/driver.py --init-db
