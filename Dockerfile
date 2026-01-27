# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app
ENV PYTHONPATH=/app/src

# Install system dependencies needed for Playwright and potential build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install-deps
RUN playwright install

# Copy project
COPY . /app/

# Set defaults for build time
ENV DJANGO_SETTINGS_MODULE=config.settings

# Collect static files during build
RUN python manage.py collectstatic --noinput

# Copy entrypoint
COPY scripts/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Start the application using Gunicorn with dynamic port
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080}"]
