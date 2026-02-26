# Accounting Project

## Overview
A robust, extensible accounting system built with Django, supporting multi-organization fiscal management, double-entry bookkeeping, and comprehensive financial reporting. Designed for clarity, auditability, and ease of use for both technical and non-technical users.

## Features
- Multi-organization support
- Fiscal year and accounting period management
- Chart of Accounts (SYSCOHADA-compliant)
- Journals and Journal Entries (double-entry)
- Entry Lines (debit/credit)
- Trial Balance, General Ledger, Balance Sheet, Income Statement
- Django admin integration
- Fine-grained permissions and roles
- Comprehensive test suite

## Tech Stack
- Python 3.10+
- Django 4.x
- SQLite (default, easily swappable)
- Bootstrap (for templates)

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd accounting_project
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the app:**
   - Main app: http://localhost:8000/
   - Admin: http://localhost:8000/admin/

## Usage
- **Admin:** Manage organizations, users, accounts, journals, entries, and periods.
- **User-facing views:**
  - Dashboard, Chart of Accounts, Journals, Journal Entries, Fiscal Years, Periods
  - Reporting: Trial Balance, General Ledger, Balance Sheet, Income Statement
- **Testing:**
   ```bash
   python manage.py test accounting
   ```

## Permissions & Roles
- Uses Django's built-in permissions system.
- Sensitive actions (create/edit/delete/post) require appropriate permissions.
- Staff and superusers have elevated access (e.g., posting entries, deleting fiscal years).
- Assign permissions via the Django admin or custom user/group management.

## App Structure
```
src/
  accounting/         # Core accounting logic (models, views, forms, admin, tests)
  reporting/          # Financial reporting views and templates
  templates/          # All HTML templates (accounting, reporting, dashboard, etc.)
  users/, organization/, ... # Supporting apps
  manage.py           # Django entry point
```

## Key Models & Business Logic
- **FiscalYear, AccountingPeriod:** Manage fiscal years and periods per organization.
- **ChartOfAccounts:** Hierarchical account structure, supports all major account types.
- **Journal, JournalEntry, EntryLine:** Double-entry bookkeeping, with posting/finalization logic.
- **Permissions:** Enforced at both view and model level for all sensitive actions.

## Reporting & Financial Statements
- **Trial Balance:** Shows opening, period, and closing balances for all accounts.
- **General Ledger:** Drill-down on all posted entry lines for any account.
- **Balance Sheet:** Summarizes assets, liabilities, and equity for a fiscal year.
- **Income Statement:** Summarizes revenues, expenses, and net income for a fiscal year.

## Contribution Guidelines
- Fork the repo and create a feature branch.
- Write clear, well-documented code and tests.
- Follow PEP8 and Django best practices.
- Submit a pull request with a clear description of your changes.

## License
[MIT License](LICENSE)

## Contact & Support
- For issues, use the GitHub issue tracker.
- For feature requests or questions, open an issue or contact the maintainers. 