#!/bin/bash
set -e

if [ "$SERVICE_ROLE" = "worker" ]; then
    echo "Running as Worker (Celery)..."
    exec celery -A config worker --loglevel=info
else
    # Run migrations
    echo "Applying database migrations..."
    python manage.py migrate

    # Execute the command passed to the docker container
    echo "Executing command: $@"
    exec "$@"
fi
