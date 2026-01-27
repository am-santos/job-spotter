#!/bin/bash
set -e

# Run migrations
echo "Applying database migrations..."
python manage.py migrate

# Execute the command passed to the docker container
echo "Executing command: $@"
exec "$@"
