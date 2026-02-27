# Architecture

This document describes the system architecture, components, and design decisions for the Accounting System.

---

## Table of Contents

1. [Overview](#overview)
2. [System Components](#system-components)
3. [Application Structure](#application-structure)
4. [Data Flow](#data-flow)
5. [Security Model](#security-model)
6. [Technology Choices](#technology-choices)

---

## Overview

The Accounting System is a multi-tenant Django application for fiscal management, double-entry bookkeeping (SYSCOHADA-compliant), and financial reporting. It is designed for organizations that require clear audit trails, role-based access control, and integration with budgets, cashflow, and fixed assets.

---

## System Components

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           External Users                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Nginx (Port 80) – Static files, reverse proxy, HTTPS termination       │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  HAProxy (Port 8080) – Load balancing for Django app instances          │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Django App (Gunicorn) – Web application, REST API, admin               │
└─────────────────────────────────────────────────────────────────────────┘
                    │                    │                    │
                    ▼                    ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ PostgreSQL   │  │    Redis     │  │ Celery       │  │ Static/Media │
│ (data store) │  │ (cache/queue)│  │ Worker + Beat│  │ (volumes)    │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### Service Roles

| Service | Purpose |
|---------|---------|
| **Nginx** | Reverse proxy, static/media serving, optional SSL |
| **HAProxy** | Load balancer for Django app instances |
| **Django (Gunicorn)** | WSGI application, business logic, templates |
| **PostgreSQL** | Primary data store |
| **Redis** | Celery broker, result backend, optional cache |
| **Celery Worker** | Background task execution |
| **Celery Beat** | Scheduled task scheduling (e.g., periodic jobs) |

---

## Application Structure

### Django Apps

| App | Responsibility |
|-----|----------------|
| **accounting** | Chart of accounts, fiscal years, periods, journals, journal entries, trial balance |
| **reporting** | General ledger, balance sheet, income statement |
| **budget** | Budgets, budget lines, commitments |
| **cashflow** | Third parties, payments, receipts, bank reconciliation |
| **assets** | Fixed assets, depreciation methods, depreciation entries |
| **organization** | Multi-tenant organizations |
| **users** | User profiles, roles, organization assignment |
| **core** | Shared mixins: `TenantAccessMixin`, `RoleRequiredMixin` |

### Key Models

| App | Model | Purpose |
|-----|-------|---------|
| accounting | `FiscalYear` | Fiscal year definition, status (Open/Closed) |
| accounting | `AccountingPeriod` | Periods within a fiscal year |
| accounting | `ChartOfAccounts` | Hierarchical chart (Asset, Liability, Equity, Revenue, Expense) |
| accounting | `Journal` | Journal definitions (Sales, Purchase, Bank, Cash, Misc, Opening) |
| accounting | `JournalEntry` | Journal entry header with posting status |
| accounting | `EntryLine` | Debit/credit lines per entry |
| budget | `Budget` | Budget per fiscal year |
| budget | `BudgetLine` | Account allocation per budget |
| budget | `BudgetCommitment` | Purchase orders, commitments |
| cashflow | `ThirdParty` | Supplier, Customer, Donor, Employee |
| cashflow | `Payment` / `Receipt` | Cash movements with journal entry creation |
| cashflow | `BankReconciliation` | Statement vs ledger reconciliation |
| assets | `FixedAsset` | Fixed asset definition, depreciation |
| assets | `DepreciationMethod` | Depreciation calculation method |
| organization | `Organization` | Tenant entity |

---

## Data Flow

### Request Flow

1. User → Nginx (HTTP/HTTPS)
2. Nginx → HAProxy (internal)
3. HAProxy → Django (Gunicorn)
4. Django: middleware → URL routing → view
5. View: permission check → tenant filter → business logic → template/response

### Multi-Tenancy

- **TenantAccessMixin**: Filters querysets by `request.user.profile.organization`
- All tenant-scoped models include an `organization` (or equivalent) foreign key
- Users are associated with one organization via `UserProfile`

### Journal Entry Posting

1. User creates a journal entry with lines (debit/credit)
2. Totals must balance (sum debits = sum credits)
3. User submits for posting
4. `JournalEntryPostView` validates and marks entry as posted
5. Entry lines become immutable after posting (audit trail)

---

## Security Model

### Authentication

- **django-allauth**: Email-based auth, optional Google OAuth
- Session-based authentication

### Authorization

- **Django permissions**: `add`, `change`, `delete`, custom (e.g. `post_journalentry`)
- **RoleRequiredMixin**: Restricts access by user role (e.g. Accountant, Admin)
- **TenantAccessMixin**: Ensures data isolation per organization

### Sensitive Operations

- Posting journal entries: `permission_required('accounting.post_journalentry')` or equivalent
- Deleting fiscal years: staff/superuser only
- Closing periods: restricted by role

---

## Technology Choices

| Technology | Rationale |
|------------|-----------|
| **Django 4.2** | Mature ORM, admin, auth, security |
| **PostgreSQL** | ACID, JSON support, scalability |
| **Redis** | Fast broker for Celery, optional caching |
| **Celery** | Async tasks, scheduled jobs (django-celery-beat) |
| **Gunicorn** | Production-grade WSGI server |
| **django-environ** | Environment-based configuration |
| **django-crispy-forms** | Consistent Bootstrap 5 forms |
| **SYSCOHADA** | West African accounting standard compatibility |
