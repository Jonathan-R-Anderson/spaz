#!/bin/bash
set -e

export PYTHONPATH=/app 

# Start anime-captcha server in background
cd /app/anime-captcha && pnpm preview &

# Ensure subsequent commands run from the application root
cd /app

# Run tests
echo "🔍 Running unit tests..."
if ! pytest -q --tb=short; then
    echo "❌ Unit tests failed. Shutting down container."
    exit 1
fi

# Start Flask app
echo "✅ All tests passed. Starting Flask server..."
exec python3 driver.py
