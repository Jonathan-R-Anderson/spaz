#!/bin/bash

# Start PostgreSQL service
service postgresql start

# Start Redis server
service redis-server start

# Wait for PostgreSQL to start
until pg_isready -h localhost; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Switch to the postgres user and create the 'admin' user and DATABASE_URL database
su - postgres -c "psql -c \"CREATE USER admin WITH PASSWORD 'admin';\""
su - postgres -c "psql -c \"ALTER USER admin WITH SUPERUSER;\""
su - postgres -c "psql -c \"CREATE DATABASE rtmp_db;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE rtmp_db TO admin;\""

# Create the magnet_urls table in DATABASE_URL
su - postgres -c "psql -d rtmp_db -c \"
CREATE TABLE IF NOT EXISTS magnet_urls (
    id SERIAL PRIMARY KEY,
    eth_address VARCHAR(255) NOT NULL,
    magnet_url TEXT NOT NULL,
    snapshot_index INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);\""

# Restart PostgreSQL to apply changes
service postgresql restart

# Wait for PostgreSQL to restart and be available again
until pg_isready -h localhost; do
  >&2 echo "Waiting for Postgres to restart - sleeping"
  sleep 1
done

# Start the Flask application
python3 app.py
