# Setup Guide

This document provides detailed setup instructions for local development and Docker-based deployment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Local Development](#local-development)
4. [Docker Setup](#docker-setup)
5. [Post-Setup](#post-setup)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Runtime |
| PostgreSQL | 14+ (optional for local) | Production database |
| Redis | 6+ (optional for local) | Celery broker |
| Docker & Docker Compose | Latest | Containerized deployment |

For local development without Docker, SQLite is used by default. PostgreSQL and Redis are optional unless you run Celery or need production parity.

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key (required in production) | `your-secret-key-here` |
| `DEBUG` | Enable debug mode | `True` (local) / `False` (production) |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost 127.0.0.1` |

### Database (PostgreSQL)

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `accounting_db` |
| `POSTGRES_USER` | Database user | `accounting_user` |
| `POSTGRES_PASSWORD` | Database password | Secure password |
| `DATABASE_URL` | Full connection URL | `postgres://user:pass@db:5432/dbname` |

For local SQLite, omit `DATABASE_URL` or use the default `sqlite:///path/to/db.sqlite3`.

### Redis & Celery

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | Same as `REDIS_URL` |
| `CELERY_RESULT_BACKEND` | Result backend URL | Same as `REDIS_URL` |

### Example `.env` (Local Development)

```env
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]

# Optional – defaults to SQLite if not set
# DATABASE_URL=postgres://user:pass@localhost:5432/accounting_db

# Optional – required only for Celery
# REDIS_URL=redis://localhost:6379/0
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## Local Development

### 1. Clone and Enter Project

```bash
git clone <repo-url>
cd accounting_project
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, DEBUG, etc.)
```

### 5. Run Migrations

```bash
python src/manage.py migrate
```

### 6. Create Superuser

```bash
python src/manage.py createsuperuser
```

### 7. Run Development Server

```bash
python src/manage.py runserver 0.0.0.0:8000
```

Or use the Makefile (from project root):

```bash
make venv      # Create venv
make install   # Install dependencies
make migrate   # Run migrations
make createsuperuser
make run       # Start server
```

Access the app at **http://localhost:8000** and admin at **http://localhost:8000/admin/**.

### Optional: Run Celery (requires Redis)

```bash
# Terminal 1 – Celery worker
celery -A config worker -l info

# Terminal 2 – Celery beat (scheduler)
celery -A config beat -l info
```

---

## Docker Setup

### 1. Build and Start Services

```bash
cp .env.example .env
# Edit .env – ensure POSTGRES_PASSWORD, SECRET_KEY are set

docker-compose up -d
```

### 2. Run Migrations

```bash
docker-compose exec app python manage.py migrate
```

### 3. Create Superuser

```bash
docker-compose exec app python manage.py createsuperuser
```

### 4. Collect Static Files (optional, for production)

```bash
docker-compose exec app python manage.py collectstatic --noinput
```

### 5. Access the Application

| Service | URL |
|---------|-----|
| Main app (via Nginx) | http://localhost |
| HAProxy | http://localhost:8080 |
| Django (direct) | Internal only |

### Docker Services

| Service | Purpose | Port |
|---------|---------|------|
| app | Django/Gunicorn | 8000 (internal) |
| db | PostgreSQL 15 | 5432 |
| redis | Redis 7 | 6379 |
| celery_worker | Celery worker | - |
| celery_beat | Celery beat | - |
| haproxy | Load balancer | 8080 |
| nginx | Reverse proxy | 80 |

---

## Post-Setup

1. **Log in to admin**: http://localhost/admin/ (or http://localhost:8000/admin/)
2. **Create an organization**: Organization → Add
3. **Create a user profile**: Link user to organization and role
4. **Create fiscal year**: Accounting → Fiscal years → Add
5. **Create chart of accounts**: Accounting → Chart of accounts → Add
6. **Create journals**: Accounting → Journals → Add

---

## Troubleshooting

### Database Connection Errors

- Ensure PostgreSQL is running and `DATABASE_URL` is correct
- For Docker: use hostname `db` (e.g. `postgres://user:pass@db:5432/dbname`)
- For local: use `localhost` in the URL

### Static Files Not Loading

- Run `python manage.py collectstatic --noinput`
- In development, `DEBUG=True` serves static files automatically
- In production, ensure Nginx serves `/static/` and `/media/`

### Celery Not Processing Tasks

- Ensure Redis is running
- Check `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
- Verify Celery worker: `celery -A config worker -l info`

### Permission Denied

- Ensure user has `UserProfile` linked to an `Organization`
- Assign appropriate roles and Django permissions
- Staff/superuser bypass most restrictions
