#!/bin/bash
set -ex

# Start Redis
service redis-server start

# Wait for PG to be ready
until pg_isready -h localhost -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

# Create tables
python3 /app/driver.py --init-db
