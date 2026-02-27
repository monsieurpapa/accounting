# API & URL Reference

This document describes the URL structure, views, and API endpoints for the Accounting System.

---

## Table of Contents

1. [URL Overview](#url-overview)
2. [Accounting Module](#accounting-module)
3. [Reporting Module](#reporting-module)
4. [Budget Module](#budget-module)
5. [Cashflow Module](#cashflow-module)
6. [Users & Organization](#users--organization)
7. [Authentication](#authentication)
8. [Django REST Framework](#django-rest-framework)

---

## URL Overview

| Prefix | Namespace | Description |
|--------|-----------|-------------|
| `/` | accounting | Dashboard, chart of accounts, journals, entries, fiscal years, periods |
| `/reporting/` | reporting | Trial balance, general ledger, balance sheet, income statement |
| `/budget/` | budget | Budgets, budget lines |
| `/cashflow/` | cashflow | Third parties, payments, receipts, bank reconciliation |
| `/users/` | users | User profiles |
| `/organization/` | organization | Organization settings |
| `/admin/` | - | Django admin |
| `/accounts/` | - | django-allauth (login, signup, logout, OAuth) |
| `/i18n/` | - | Django internationalization (language switcher) |

**Note:** The `assets` app (fixed assets) has URL configuration but is not currently included in the root URLconf. To expose it, add `path('assets/', include(('assets.urls', 'assets'), namespace='assets'))` to `config/urls.py`.

---

## Accounting Module

Base URL: `/` (namespace: `accounting`)

| URL | View | Description |
|-----|------|-------------|
| `/` | dashboard | Main dashboard |
| `/journals/` | journals | Journal overview |
| `/journal-entries/` | journal_entries | Journal entries list |
| `/journal-entries/create/` | journal_entry_create | Create journal entry |
| `/chart-of-accounts/` | chart_of_accounts | Chart of accounts overview |
| `/trial-balance/` | trial_balance | Trial balance report |
| `/accounts/` | ChartOfAccountsListView | List chart of accounts |
| `/accounts/create/` | ChartOfAccountsCreateView | Create account |
| `/accounts/<uuid>/` | ChartOfAccountsDetailView | Account detail |
| `/accounts/<uuid>/edit/` | ChartOfAccountsUpdateView | Edit account |
| `/accounts/<uuid>/delete/` | ChartOfAccountsDeleteView | Delete account |
| `/journals/list/` | JournalListView | List journals |
| `/journals/create/` | JournalCreateView | Create journal |
| `/journals/<uuid>/` | JournalDetailView | Journal detail |
| `/journals/<uuid>/edit/` | JournalUpdateView | Edit journal |
| `/journals/<uuid>/delete/` | JournalDeleteView | Delete journal |
| `/journal-entry/list/` | JournalEntryListView | List journal entries |
| `/journal-entry/create/` | JournalEntryCreateView | Create journal entry |
| `/journal-entry/<uuid>/` | JournalEntryDetailView | Journal entry detail |
| `/journal-entry/<uuid>/edit/` | JournalEntryUpdateView | Edit journal entry |
| `/journal-entry/<uuid>/delete/` | JournalEntryDeleteView | Delete journal entry |
| `/journal-entry/<uuid>/post/` | JournalEntryPostView | Post journal entry |
| `/fiscalyears/` | FiscalYearListView | List fiscal years |
| `/fiscalyears/create/` | FiscalYearCreateView | Create fiscal year |
| `/fiscalyears/<uuid>/` | FiscalYearDetailView | Fiscal year detail |
| `/fiscalyears/<uuid>/edit/` | FiscalYearUpdateView | Edit fiscal year |
| `/fiscalyears/<uuid>/delete/` | FiscalYearDeleteView | Delete fiscal year |
| `/fiscalyear/<uuid>/periods/` | AccountingPeriodListView | List periods |
| `/fiscalyear/<uuid>/periods/create/` | AccountingPeriodCreateView | Create period |
| `/periods/<uuid>/` | AccountingPeriodDetailView | Period detail |
| `/periods/<uuid>/edit/` | AccountingPeriodUpdateView | Edit period |
| `/periods/<uuid>/delete/` | AccountingPeriodDeleteView | Delete period |
| `/periods/<uuid>/close/` | AccountingPeriodCloseView | Close period |

---

## Reporting Module

Base URL: `/reporting/` (namespace: `reporting`)

| URL | View | Description |
|-----|------|-------------|
| `/` | reporting_index | Reporting index |
| `/general-ledger/` | general_ledger | General ledger report |
| `/balance-sheet/` | balance_sheet | Balance sheet report |
| `/income-statement/` | income_statement | Income statement report |
| `/trial-balance/` | trial_balance | Trial balance report |

**Query Parameters (reporting views):**

- `account` – Account UUID (general ledger)
- `fiscal_year` – Fiscal year UUID
- `period` – Accounting period UUID

---

## Budget Module

Base URL: `/budget/` (namespace: `budget`)

| URL | View | Description |
|-----|------|-------------|
| `/` | BudgetListView | List budgets |
| `/create/` | BudgetCreateView | Create budget |
| `/<uuid>/` | BudgetDetailView | Budget detail |
| `/<uuid>/edit/` | BudgetUpdateView | Edit budget |
| `/<uuid>/delete/` | BudgetDeleteView | Delete budget |
| `/lines/create/` | BudgetLineCreateView | Create budget line |
| `/lines/<uuid>/edit/` | BudgetLineUpdateView | Edit budget line |
| `/lines/<uuid>/delete/` | BudgetLineDeleteView | Delete budget line |

---

## Cashflow Module

Base URL: `/cashflow/` (namespace: `cashflow`)

| URL | View | Description |
|-----|------|-------------|
| Third parties | ThirdPartyListView, CreateView, DetailView, UpdateView, DeleteView | CRUD for third parties |
| Payments | PaymentListView, CreateView, DetailView, UpdateView, DeleteView | CRUD for payments |
| Receipts | ReceiptListView, CreateView, DetailView, UpdateView, DeleteView | CRUD for receipts |
| Bank reconciliation | BankReconciliationListView, CreateView, DetailView, UpdateView, DeleteView | Bank reconciliation CRUD |

---

## Users & Organization

| URL | Description |
|-----|-------------|
| `/users/profile/` | User profile view/edit |
| `/organization/settings/` | Organization settings |

---

## Authentication

django-allauth handles authentication under `/accounts/`:

| URL | Description |
|-----|-------------|
| `/accounts/login/` | Log in |
| `/accounts/signup/` | Sign up |
| `/accounts/logout/` | Log out |
| `/accounts/password/change/` | Change password |
| `/accounts/password/reset/` | Password reset |
| `/accounts/google/login/` | Google OAuth (if configured) |

---

## Django REST Framework

Django REST Framework is installed but no API routes are currently defined in the URLconf. To add REST API support:

1. Create serializers for models
2. Create API views (ViewSets or APIViews)
3. Register routes in `config/urls.py` or a dedicated API app
