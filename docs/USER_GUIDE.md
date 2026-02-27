# User Guide — TicTacFlow Accounting Portal

This user guide explains the system for both accountants and non-accountants and documents the full workflow for typical tasks. Follow the table of contents to jump to relevant sections.

## Table of Contents

- 1. Getting Started
  - 1.1 Who’s Who
  - 1.2 Logging In
  - 1.3 Profile & Organisation
- 2. Overview of the Interface
  - 2.1 Vertical Navbar
- 3. Accounting Features (Workflows)
  - 3.1 Chart of Accounts — Setup & Maintenance
  - 3.2 Journals & Journal Entries — Full Workflow
  - 3.3 Viewing, Filtering, Exporting Entries
- 4. Reporting — Generate & Export
- 5. Budgeting — Plan & Review
- 6. Cash Flow — Record Payments & Receipts
- 7. Administration (Super-users) — Users & Organisations
  - 7.1 Users: CRUD workflow
  - 7.2 Organisations: CRUD workflow
  - 7.3 Bulk population via management commands
- 8. Tips for Non-Accountants
- 9. Glossary
- 10. Troubleshooting
- 11. Further Resources

---

## 1. Getting Started

### 1.1 Who’s Who

- Accountant / Financial user — responsible for configuring the chart of accounts, preparing journals and reports.
- Regular (non-accountant) user — creates simple cash flow records, submits entries, and manages personal profile.
- Super-user (administrator) — manages users and organisations and may perform all accountant tasks.

### 1.2 Logging In

1. Open the app at `http://<host>/accounts/login/`.
2. Enter credentials (email/username and password). If you don't have an account, register via `Register` and ask an administrator to enable it.

### 1.3 Profile & Organisation

- Open the **Profile** page to view and edit your personal information, role and organisation (where allowed).

---

## 2. Overview of the Interface

### 2.1 Vertical Navbar

The left navigation links to the major sections: Dashboard, Accounting, Reporting, Budgeting, Cash Flow and Administration (Admin visible to super-users only).

---

## 3. Accounting Features (Workflows)

### 3.1 Chart of Accounts — Setup & Maintenance (Accountant)

Purpose: Create the account structure before transactions are posted.

Steps:

1. Navigate to `Accounting → Chart of Accounts`.
2. Click `Add account`.
3. Fill: `Name`, `Code`, `Type` (Asset/Liability/Equity/Expense/Income), `Parent` (optional).
4. Save. Use `Edit` to change or `Delete` to remove (delete is limited to accounts with no dependent entries).

Notes for non-accountants: consult your accountant before adding or editing accounts.

### 3.2 Journals & Journal Entries — Full Workflow (Accountant)

Purpose: Record double-entry transactions grouped by journals.

Create a Journal

1. Accounting → Journals → `Add journal`.
2. Name, Description, Default reference.

Create a Journal Entry

1. Select the target journal.
2. Click `New entry`.
3. Enter:
   - Date
   - Reference
   - Description
   - Line items: account, debit/credit, description
4. Ensure the entry balances (debits = credits) — the UI enforces this.
5. Save to post.

Edit / Delete

- Use `Edit` to correct unposted or recent entries (depending on your organisation rules).
- Use `Delete` only when permitted; historical audit rules may restrict deletion.

### 3.3 Viewing, Filtering & Exporting Entries

- Use filters (date range, account, journal) to narrow results.
- Export to PDF or CSV from the report dropdown.

---

## 4. Reporting — Generate & Export (Accountant)

Key reports: Trial Balance, Income Statement, Balance Sheet.

Steps:

1. Reporting → select report type.
2. Choose fiscal year and period.
3. Click `Generate`.
4. Export via the PDF or CSV options.

---

## 5. Budgeting — Plan & Review

Workflow:

1. Budgeting → `Add budget`.
2. Assign account(s), amount, start/end period.
3. Compare actuals in budget reports.

---

## 6. Cash Flow — Record Payments & Receipts (Non-Accountant Friendly)

Workflow:

1. Cash Flow → `Payments & Receipts`.
2. Click `Add`.
3. Select type (Payment or Receipt), date, counterpart, account, amount.
4. Save — the transaction will optionally create a linked journal entry.

Notes: If you don't see an account you expect, ask your accountant to add it to the Chart of Accounts.

---

## 7. Administration (Super-users)

> Administration features are visible only to users with the `is_superuser` flag.

### 7.1 Users: CRUD workflow

- Navigate: Admin → Users
- `Add user` → create a user and optionally assign organization and role
- `View` → see read-only details
- `Edit` → change user attributes or roles
- `Delete` → remove the user (careful with audit trail implications)

Management commands for bulk creation live in `src/users/management/commands/populate_users.py`.

### 7.2 Organisations: CRUD workflow

- Admin → Organizations
- Add/Edit/Delete organizations; these group users and may influence data visibility

### 7.3 Bulk population via management commands

To populate users or organizations from JSON files, run:

```bash
python src/manage.py populate_users path/to/users.json
python src/manage.py populate_organizations path/to/orgs.json
```

Refer to the command source for expected JSON structure.

---

## 8. Tips for Non-Accountants

- Use simple Cash Flow entries if unfamiliar with double-entry accounting.
- Always add a helpful description on entries to make accountant reviews easier.

---

## 9. Glossary

- **Account** — ledger category.
- **Journal** — collection of related entries.
- **Entry** — set of debit/credit lines.

---

## 10. Troubleshooting

- Permission errors: check your account or ask an admin.
- Template errors: contact the development team and provide the full stack trace.

---

## 11. Further Resources

- Developer docs: `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/SETUP.md`.

---

### Full Workflow Example: Recording a Customer Payment and Reconciling

1. Accountant sets up `Accounts Receivable` and `Bank` accounts in Chart of Accounts.
2. Non-accountant records a Receipt under Cash Flow → `Add` with account `Bank` and links an invoice reference.
3. System creates a journal entry (if configured) crediting sales and debiting bank.
4. Accountant reviews journal entries, reconciles receipts, and runs `Reporting → Income Statement`.

---

*Document created automatically by the development assistant. For printable versions (PDF), render this Markdown using your preferred tool.*
