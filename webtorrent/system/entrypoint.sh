#!/bin/bash

set -e  # Exit immediately on error

echo "[ENTRYPOINT] Running tests..."
pytest tests/

echo "[ENTRYPOINT] Tests passed. Starting application..."
exec python3 driver.py
