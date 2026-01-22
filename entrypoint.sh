#!/bin/bash
set -e

# Run migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
# Bind to 0.0.0.0:$PORT (default 8080 used by Cloud Run)
PORT=${PORT:-8000}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
