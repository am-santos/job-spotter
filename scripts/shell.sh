#!/bin/bash
set -e

# Help / Usage
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "Usage: ./shell.sh [--reset-db]"
    echo "  --reset-db  : Destroys the database volume before starting (Fresh DB)"
    exit 0
fi

# Reset DB if requested
if [ "$1" == "--reset-db" ]; then
    echo "⚠️  WARNING: Resetting database... All data will be lost."
    docker-compose down -v
    echo "Database volume removed."
fi

# Ensure we have the latest build (optional but good for 'most updated code')
# We only rebuild if strictly necessary or user asks?
# 'docker-compose run' doesn't build by default.
# Let's assume user wants fast startup, but they said "using most updated code".
# Code updates are mounted. Only dependency updates need build.
# We'll skip forced build for speed, user can run 'docker-compose build' if they changed requirements.
# OR we can add a simple check. Let's just run it.

echo "Starting Django Shell..."
# This runs 'entrypoint.sh' (migrations) -> 'python manage.py shell'
docker-compose run --rm web python manage.py shell
