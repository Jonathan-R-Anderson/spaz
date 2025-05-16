#!/bin/bash
set -e

echo "🔍 Running unit tests..."
if ! pytest -q --tb=short; then
    echo "❌ Unit tests failed. Shutting down container."
    exit 1
fi

echo "✅ All tests passed. Starting Flask server..."
exec python3 driver.py
