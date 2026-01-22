#!/bin/bash
set -e

# Run migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the docker container
echo "Executing command: $@"
exec "$@"
