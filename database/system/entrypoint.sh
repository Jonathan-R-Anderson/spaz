#!/bin/bash
set -ex
echo "💥 [entrypoint] Starting services"

# Start redis
service redis-server start

chmod 0700 /var/lib/postgresql/data
chown -R postgres:postgres /var/lib/postgresql/data

# Start Postgres in background
su - postgres -c "/usr/lib/postgresql/13/bin/postgres -D /var/lib/postgresql/data" &
PG_PID=$!

# Wait for Postgres to be ready
until pg_isready -h localhost -U "$POSTGRES_USER"; do
  echo "⏳ Waiting for PostgreSQL..."
  sleep 1
done

# Init DB if needed
python3 /app/driver.py --init-db

# Start Flask API (or run tests)
python3 /app/driver.py &

# Wait for background processes
wait $PG_PID
