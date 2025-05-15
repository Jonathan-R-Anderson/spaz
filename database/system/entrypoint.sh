#!/bin/bash

set -e

export PYTHONPATH=/app

# Start PostgreSQL and Redis
service postgresql start
service redis-server start

# Wait for PostgreSQL to become available
until pg_isready -h localhost -p 5432 -U postgres; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Create DB user, database, and base table if needed
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='admin'\" | grep -q 1 || psql -c \"CREATE USER admin WITH PASSWORD 'admin';\""
su - postgres -c "psql -c \"ALTER USER admin WITH SUPERUSER;\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='rtmp_db'\" | grep -q 1 || psql -c \"CREATE DATABASE rtmp_db;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE rtmp_db TO admin;\""

# Restart PostgreSQL and wait again to ensure it's ready
service postgresql restart
until pg_isready -h localhost -p 5432 -U postgres; do
  >&2 echo "Waiting for Postgres to restart - sleeping"
  sleep 1
done

# Ensure tables are created from SQLAlchemy models
echo "Creating database tables from SQLAlchemy models..."
python3 -c "
from driver import app
from extensions import db
import models.user, models.magnet
with app.app_context():
    db.create_all()
"

# Start Flask app in the background
echo "Starting Flask app for testing..."
python3 driver.py &

FLASK_PID=$!

# Wait for Flask port to open
until nc -z localhost 5003; do
  >&2 echo "Waiting for Flask app to start..."
  sleep 1
done

# Run unit tests
echo "Running unit tests..."
if ! pytest tests/; then
  echo "❌ Tests failed. Shutting down Flask app and container..."
  kill $FLASK_PID
  wait $FLASK_PID
  exit 1
fi

echo "✅ All tests passed. Bringing Flask app to foreground..."
wait $FLASK_PID
