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

# Create DB user and database
su - postgres -c "psql -c \"CREATE USER admin WITH PASSWORD 'admin';\""
su - postgres -c "psql -c \"ALTER USER admin WITH SUPERUSER;\""
su - postgres -c "psql -c \"CREATE DATABASE rtmp_db;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE rtmp_db TO admin;\""

# Create magnet_urls table if not exists
su - postgres -c "psql -d rtmp_db -c \"
CREATE TABLE IF NOT EXISTS magnet_urls (
    id SERIAL PRIMARY KEY,
    eth_address VARCHAR(255) NOT NULL,
    magnet_url TEXT NOT NULL,
    snapshot_index INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);\""

# Restart PostgreSQL
service postgresql restart

# Wait for PostgreSQL again
until pg_isready -h localhost; do
  >&2 echo "Waiting for Postgres to restart - sleeping"
  sleep 1
done

# Run unit tests
echo "Running unit tests..."
pytest tests/
TEST_STATUS=$?

if [ $TEST_STATUS -ne 0 ]; then
  echo "❌ Tests failed. Flask app will NOT start."
  exit 1
fi

echo "✅ All tests passed. Starting Flask app..."
python3 app.py
