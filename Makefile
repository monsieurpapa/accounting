# Makefile for Django Accounting Project

# Variables
PYTHON=python
PIP=pip
MANAGE=$(PYTHON) src/manage.py
VENV=.venv

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  venv            Create virtual environment"
	@echo "  install         Install dependencies"
	@echo "  migrate         Run Django migrations"
	@echo "  createsuperuser Create a Django superuser"
	@echo "  run             Run the development server"
	@echo "  test            Run all tests"
	@echo "  lint            Run flake8 linter"
	@echo "  shell           Open Django shell"
	@echo "  clean           Remove .pyc files and __pycache__"

# Create virtual environment
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV)

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Run migrations
.PHONY: migrate
migrate:
	$(MANAGE) migrate

# Create superuser
.PHONY: createsuperuser
createsuperuser:
	$(MANAGE) createsuperuser

# Run development server
.PHONY: run
run:
	$(MANAGE) runserver 0.0.0.0:8000

# Run tests
.PHONY: test
test:
	$(MANAGE) test

# Lint code
.PHONY: lint
lint:
	flake8 src/

# Open Django shell
.PHONY: shell
shell:
	$(MANAGE) shell

# Clean up .pyc and __pycache__
.PHONY: clean
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -exec rm -rf {} + 