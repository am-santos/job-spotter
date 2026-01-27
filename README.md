# Job Spotter

## Setup & Running (Hybrid Mode)

This project is configured for a **Hybrid Development** workflow:

- **Django App**: Runs locally on your host machine.
- **Database (Postgres) & Redis**: Run in Docker containers.

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Virtualenv

### 1. Start Background Services

Start Postgres and Redis. They will be exposed on ports `1111` and `2222` respectively.

```bash
docker-compose up -d db redis
```

### 2. Configure Local Environment

Ensure you have a `.env.local` file in the project root. It should look like this:

```bash
DEBUG=True
SECRET_KEY=insecure-key
DB_HOST=localhost
DB_PORT=1111
POSTGRES_DB=job_spotter
POSTGRES_USER=user
POSTGRES_PASSWORD=password
CELERY_BROKER_URL=redis://localhost:2222
CELERY_RESULT_BACKEND=redis://localhost:2222
```

### 3. Run the Application

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Migrations
python manage.py migrate

# Start Server
python manage.py runserver
```

The application will be available at [http://localhost:8000](http://localhost:8000).
