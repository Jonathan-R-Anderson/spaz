#!/bin/bash
set -e
export PYTHONPATH=/app

# Start PostgreSQL and Redis
service postgresql start
service redis-server start

# Wait for PostgreSQL
until pg_isready -h localhost -p 5432 -U postgres; do
  >&2 echo "Waiting for PostgreSQL to become available..."
  sleep 1
done

# Create DB user and database if missing
su - postgres -c "psql -tc \"SELECT 1 FROM pg_roles WHERE rolname='admin'\" | grep -q 1 || psql -c \"CREATE USER admin WITH PASSWORD 'admin';\""
su - postgres -c "psql -c \"ALTER USER admin WITH SUPERUSER;\""
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname='rtmp_db'\" | grep -q 1 || psql -c \"CREATE DATABASE rtmp_db;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE rtmp_db TO admin;\""

# Restart PostgreSQL to apply
service postgresql restart
until pg_isready -h localhost -p 5432 -U postgres; do
  >&2 echo "Waiting for PostgreSQL to restart..."
  sleep 1
done

# 💡 Create all tables using app context
echo "⏳ Creating database tables..."
python3 -c "
from driver import create_app
from extensions import db
import models.user, models.magnet

app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Tables created')
"

# Start Flask app in background
echo "🚀 Starting Flask app..."
python3 driver.py &

FLASK_PID=$!

# Wait for it to be up
until nc -z localhost 5003; do
  >&2 echo "Waiting for Flask app to start..."
  sleep 1
done

# Run tests
echo "🧪 Running tests..."
if ! pytest tests/; then
  echo "❌ Tests failed. Shutting down..."
  kill $FLASK_PID
  wait $FLASK_PID
  exit 1
fi

echo "✅ All tests passed. Running Flask in foreground..."
wait $FLASK_PID
