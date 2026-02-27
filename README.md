# Accounting System

[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A robust, extensible accounting system built with Django, supporting multi-organization fiscal management, double-entry bookkeeping (SYSCOHADA-compliant), and comprehensive financial reporting.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Development](#development)
- [License](#license)

---

## Features

| Category | Capabilities |
|----------|--------------|
| **Accounting** | Chart of accounts (SYSCOHADA), fiscal years, periods, journals, journal entries, double-entry bookkeeping |
| **Reporting** | Trial balance, general ledger, balance sheet, income statement |
| **Budget** | Budgets, budget lines, commitments (purchase orders) |
| **Cashflow** | Third parties, payments, receipts, bank reconciliation |
| **Assets** | Fixed assets, depreciation methods, depreciation entries |
| **Multi-tenant** | Organization-based isolation with role-based access control |

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│  HAProxy    │────▶│   Django    │
│  (Port 80)  │     │ (Load Bal.) │     │  (Gunicorn) │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    ▼                          ▼                          ▼
             ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
             │ PostgreSQL  │            │    Redis    │            │   Celery    │
             │   (db)      │            │   (broker)  │            │  Worker/Beat│
             └─────────────┘            └─────────────┘            └─────────────┘
```

**Tech Stack:** Django 4.2 · PostgreSQL 15 · Redis 7 · Celery · Gunicorn · Nginx · HAProxy

---

## Quick Start

### Using Docker (recommended)

```bash
# Clone the repository
git clone <repo-url>
cd accounting_project

# Configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY, POSTGRES_PASSWORD, etc.

# Start all services
docker-compose up -d

# Run migrations (first run)
docker-compose exec app python manage.py migrate

# Create superuser
docker-compose exec app python manage.py createsuperuser
```

Access the application at **http://localhost** (Nginx) or **http://localhost:8080** (HAProxy).

### Local development

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or use .env)
export DEBUG=True SECRET_KEY=dev-key-here

# Run migrations (SQLite by default)
python src/manage.py migrate

# Create superuser
python src/manage.py createsuperuser

# Run development server
python src/manage.py runserver 0.0.0.0:8000
```

Or use the Makefile:

```bash
make venv install migrate createsuperuser
make run
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, components, data flow, security |
| [docs/SETUP.md](docs/SETUP.md) | Detailed setup: local, Docker, environment variables |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Development workflow, testing, code style, Makefile |
| [docs/API.md](docs/API.md) | URL structure, views, and API overview |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment checklist and considerations |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines and pull request process |

---

## Development

| Command | Description |
|---------|-------------|
| `make run` | Start development server |
| `make test` | Run all tests |
| `make migrate` | Apply database migrations |
| `make shell` | Open Django shell |
| `make lint` | Run flake8 linter |

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for full details.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Support

- **Issues:** [GitHub Issue Tracker](https://github.com/your-org/accounting_project/issues)
- **Contact:** See repository maintainers for support.
