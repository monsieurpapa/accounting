# Development Guide

This document covers development workflow, testing, code style, and conventions for the Accounting System.

---

## Table of Contents

1. [Development Workflow](#development-workflow)
2. [Makefile Targets](#makefile-targets)
3. [Testing](#testing)
4. [Code Style](#code-style)
5. [Project Structure](#project-structure)
6. [Migrations](#migrations)
7. [Debugging](#debugging)

---

## Development Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** following [Code Style](#code-style)

3. **Run tests** before committing:
   ```bash
   make test
   ```

4. **Commit with clear messages**:
   ```bash
   git add .
   git commit -m "Add: description of change"
   ```

5. **Push and open a pull request**

---

## Makefile Targets

Run from project root. Ensure virtual environment is activated if using `make install`, `make run`, etc.

| Target | Command | Description |
|--------|---------|-------------|
| `help` | `make help` | List available targets |
| `venv` | `make venv` | Create virtual environment (`.venv`) |
| `install` | `make install` | Install requirements |
| `migrate` | `make migrate` | Run Django migrations |
| `createsuperuser` | `make createsuperuser` | Create superuser |
| `run` | `make run` | Run development server (0.0.0.0:8000) |
| `test` | `make test` | Run all tests |
| `lint` | `make lint` | Run flake8 on `src/` |
| `shell` | `make shell` | Open Django shell |
| `clean` | `make clean` | Remove `*.pyc` and `__pycache__` |

**Variables** (override in Makefile or command line):

- `PYTHON` – Python executable
- `MANAGE` – Django manage.py path
- `VENV` – Virtual environment directory

---

## Testing

### Run All Tests

```bash
python src/manage.py test
# or
make test
```

### Run Tests by App

```bash
python src/manage.py test accounting
python src/manage.py test reporting
python src/manage.py test budget
```

### Run Tests by Module

```bash
python src/manage.py test accounting.tests
```

### Run with Coverage (if coverage is installed)

```bash
pip install coverage
coverage run src/manage.py test
coverage report
coverage html  # Generate htmlcov/
```

---

## Code Style

### Python (PEP 8)

- Follow [PEP 8](https://pep8.org/)
- Use `flake8` for linting: `make lint`
- Maximum line length: 88 (Black) or 120 (configurable in flake8)

### Django Conventions

- **Models**: Use `uuid` for primary keys where appropriate (UUID4)
- **Views**: Prefer class-based views (CBV) with mixins (`TenantAccessMixin`, `RoleRequiredMixin`)
- **Forms**: Use `django-crispy-forms` with `crispy_bootstrap5`
- **URLs**: Use namespaced URL patterns (e.g. `accounting:journal_detail`)
- **Templates**: Place in `templates/<app_name>/` or `templates/` as per `TEMPLATES` config

### Docstrings

- Use docstrings for modules, classes, and public functions
- Follow Google or NumPy style (be consistent within the project)

### Template Best Practices

- Use `{% trans %}` or `{% translate %}` for translatable strings
- Add spaces around `==` in `{% if %}`: `{% if a == b %}`
- Use `date` filter with formats matching the object type (date vs datetime)

---

## Project Structure

```
accounting_project/
├── src/                    # Application source
│   ├── manage.py
│   ├── config/             # Django project config
│   ├── accounting/         # Core accounting
│   ├── assets/
│   ├── budget/
│   ├── cashflow/
│   ├── core/               # Shared mixins
│   ├── organization/
│   ├── reporting/
│   ├── users/
│   ├── templates/
│   └── static_src/
├── docker/
│   ├── django/
│   ├── nginx/
│   └── haproxy/
├── docs/                   # Documentation
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── Makefile
└── README.md
```

---

## Migrations

### Create Migrations

```bash
python src/manage.py makemigrations
# or by app
python src/manage.py makemigrations accounting
```

### Apply Migrations

```bash
python src/manage.py migrate
make migrate
```

### Inspect Migrations

```bash
python src/manage.py showmigrations
```

### Squash Migrations (optional)

For long migration history:

```bash
python src/manage.py squashmigrations accounting 0001
```

---

## Debugging

### Django Debug Toolbar (optional)

Add to `INSTALLED_APPS`:

```python
'debug_toolbar',
```

Add to middleware and URLs per [django-debug-toolbar docs](https://django-debug-toolbar.readthedocs.io/).

### Logging

Configure in `config/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
```

### Shell

```bash
python src/manage.py shell
# or
make shell
```

For IPython: `pip install ipython` and use `python src/manage.py shell`.
