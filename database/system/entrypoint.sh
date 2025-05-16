#!/bin/bash
set -ex

echo "💥 [entrypoint] Starting services"

# Start Redis
service redis-server start

# Set permissions
chmod 0700 /var/lib/postgresql/data
chown -R postgres:postgres /var/lib/postgresql/data

# Initialize DB if missing
if [ ! -f /var/lib/postgresql/data/PG_VERSION ]; then
  echo "⚙️ Initializing PostgreSQL database..."
  rm -rf /var/lib/postgresql/data/*
  su - postgres -c "/usr/lib/postgresql/13/bin/initdb -D /var/lib/postgresql/data"
fi

# Start Postgres in background
su - postgres -c "/usr/lib/postgresql/13/bin/postgres -D /var/lib/postgresql/data" &
PG_PID=$!

# Wait for Postgres to be ready
until pg_isready -h localhost -U postgres; do
  echo "⏳ Waiting for PostgreSQL..."
  sleep 1
done

# Create admin role and rtmp_db if not present
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'\" | grep -q 1 || psql -c \"CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';\""
su - postgres -c "psql -c \"ALTER USER ${POSTGRES_USER} WITH SUPERUSER;\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'\" | grep -q 1 || psql -c \"CREATE DATABASE ${POSTGRES_DB};\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'\" | grep -q 1 || psql -c \"CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';\""
su - postgres -c "psql -c \"ALTER USER ${POSTGRES_USER} WITH SUPERUSER;\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='${POSTGRES_DB}'\" | grep -q 1 || psql -c \"CREATE DATABASE ${POSTGRES_DB};\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};\""

# Run your app's DB setup script (SQLAlchemy etc.)
python3 /app/driver.py --init-db

# Optionally run the Flask server (or background job)
python3 /app/driver.py &

# Wait for background Postgres
wait $PG_PID
