# Contributing to Accounting System

Thank you for your interest in contributing. This document outlines the process and guidelines for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Pull Request Process](#pull-request-process)
5. [Coding Standards](#coding-standards)
6. [Testing Requirements](#testing-requirements)
7. [Documentation](#documentation)

---

## Code of Conduct

- Be respectful and constructive
- Focus on the code and ideas, not on individuals
- Follow project conventions and best practices

---

## How to Contribute

### Reporting Issues

- Use the [GitHub Issue Tracker](https://github.com/your-org/accounting_project/issues)
- Search existing issues before creating a new one
- Provide: steps to reproduce, expected vs actual behavior, environment details
- For bugs: include error messages, stack traces, and relevant logs

### Suggesting Features

- Open an issue with the `enhancement` label
- Describe the use case and proposed solution
- Discuss implementation options before submitting code

### Submitting Code

1. Fork the repository
2. Create a feature branch from `main`
3. Implement your changes with tests
4. Ensure tests pass and lint is clean
5. Open a pull request

---

## Development Setup

See [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

```bash
git clone https://github.com/your-org/accounting_project.git
cd accounting_project
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python src/manage.py migrate
python src/manage.py createsuperuser
```

---

## Pull Request Process

1. **Update from main** before submitting:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run tests and lint**:
   ```bash
   make test
   make lint
   ```

3. **Submit PR** with:
   - Clear title and description
   - Reference to related issue(s) (e.g. "Fixes #123")
   - Summary of changes
   - Screenshots if UI-related

4. **Review**: Address feedback from maintainers

5. **Merge**: Maintainers will merge after approval

---

## Coding Standards

- **Python**: PEP 8, max line length 88–120
- **Django**: Follow Django best practices; prefer CBVs and mixins
- **Templates**: Use `{% trans %}` for translatable text; add spaces around `==` in `{% if %}`
- **Imports**: Standard library → third-party → local, alphabetized
- **Docstrings**: Add docstrings for modules, classes, and public functions

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for more detail.

---

## Testing Requirements

- New features should include tests
- Bug fixes should include a regression test
- Run full test suite before submitting: `make test`
- Tests live in `tests.py` or `tests/` within each app

---

## Documentation

- Update relevant docs when changing behavior
- Add docstrings to new modules, classes, and public functions
- Update [docs/API.md](docs/API.md) if adding or changing URLs
- Update [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for architectural changes

---

## Questions?

Open an issue or contact the maintainers. Thank you for contributing!
