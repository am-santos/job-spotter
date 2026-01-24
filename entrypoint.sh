#!/bin/bash
set -e

if [ "$SERVICE_ROLE" = "worker" ]; then
    echo "Running as Worker (Celery)..."
    echo "Celery is not configured yet. Skipping command: 'exec celery -A config worker --loglevel=info'"
    #exec celery -A config worker --loglevel=info
else
    # Run migrations
    echo "Applying database migrations..."
    python manage.py migrate

    # Execute the command passed to the docker container
    echo "Executing command: $@"
    exec "$@"
fi
