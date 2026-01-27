#!/bin/bash
set -e

# Start Celery worker
echo "Starting Celery worker..."
celery -A config worker --loglevel=info
