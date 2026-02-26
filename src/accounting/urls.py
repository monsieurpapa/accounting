from django.urls import path
from . import views
from .views import (
    ChartOfAccountsListView, ChartOfAccountsCreateView, ChartOfAccountsUpdateView,
    ChartOfAccountsDeleteView, ChartOfAccountsDetailView,
    JournalListView, JournalCreateView, JournalUpdateView,
    JournalDeleteView, JournalDetailView,
    JournalEntryListView, JournalEntryCreateView, JournalEntryUpdateView,
    JournalEntryDeleteView, JournalEntryDetailView,
    JournalEntryPostView,
    FiscalYearListView, FiscalYearCreateView, FiscalYearUpdateView, FiscalYearDeleteView, FiscalYearDetailView,
    AccountingPeriodListView, AccountingPeriodCreateView, AccountingPeriodUpdateView, AccountingPeriodDeleteView, AccountingPeriodDetailView,
    AccountingPeriodCloseView
)

app_name = 'accounting'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('journals/', views.journals, name='journals'),
    path('journal-entries/', views.journal_entries, name='journal_entries'),
    path('journal-entries/create/', views.journal_entry_create, name='journal_entry_create'),
    path('chart-of-accounts/', views.chart_of_accounts, name='chart_of_accounts'),
    path('trial-balance/', views.trial_balance, name='trial_balance'),
    path('accounts/', ChartOfAccountsListView.as_view(), name='chart_of_accounts_list'),
    path('accounts/create/', ChartOfAccountsCreateView.as_view(), name='chart_of_accounts_create'),
    path('accounts/<uuid:uuid>/edit/', ChartOfAccountsUpdateView.as_view(), name='chart_of_accounts_edit'),
    path('accounts/<uuid:uuid>/delete/', ChartOfAccountsDeleteView.as_view(), name='chart_of_accounts_delete'),
    path('accounts/<uuid:uuid>/', ChartOfAccountsDetailView.as_view(), name='chart_of_accounts_detail'),
    path('journals/list/', JournalListView.as_view(), name='journal_list'),
    path('journals/create/', JournalCreateView.as_view(), name='journal_create'),
    path('journals/<uuid:uuid>/edit/', JournalUpdateView.as_view(), name='journal_edit'),
    path('journals/<uuid:uuid>/delete/', JournalDeleteView.as_view(), name='journal_delete'),
    path('journals/<uuid:uuid>/', JournalDetailView.as_view(), name='journal_detail'),
    path('journal-entry/list/', JournalEntryListView.as_view(), name='journal_entry_list'),
    path('journal-entry/create/', JournalEntryCreateView.as_view(), name='journal_entry_create_cbv'),
    path('journal-entry/<uuid:uuid>/edit/', JournalEntryUpdateView.as_view(), name='journal_entry_edit'),
    path('journal-entry/<uuid:uuid>/delete/', JournalEntryDeleteView.as_view(), name='journal_entry_delete'),
    path('journal-entry/<uuid:uuid>/', JournalEntryDetailView.as_view(), name='journal_entry_detail'),
    path('journal-entry/<uuid:uuid>/post/', JournalEntryPostView.as_view(), name='journal_entry_post'),
    path('fiscalyears/', FiscalYearListView.as_view(), name='fiscalyear_list'),
    path('fiscalyears/create/', FiscalYearCreateView.as_view(), name='fiscalyear_create'),
    path('fiscalyears/<uuid:uuid>/edit/', FiscalYearUpdateView.as_view(), name='fiscalyear_edit'),
    path('fiscalyears/<uuid:uuid>/delete/', FiscalYearDeleteView.as_view(), name='fiscalyear_delete'),
    path('fiscalyears/<uuid:uuid>/', FiscalYearDetailView.as_view(), name='fiscalyear_detail'),
    path('fiscalyear/<uuid:uuid>/periods/', AccountingPeriodListView.as_view(), name='accountingperiod_list'),
    path('fiscalyear/<uuid:uuid>/periods/create/', AccountingPeriodCreateView.as_view(), name='accountingperiod_create'),
    path('periods/<uuid:uuid>/edit/', AccountingPeriodUpdateView.as_view(), name='accountingperiod_edit'),
    path('periods/<uuid:uuid>/delete/', AccountingPeriodDeleteView.as_view(), name='accountingperiod_delete'),
    path('periods/<uuid:uuid>/', AccountingPeriodDetailView.as_view(), name='accountingperiod_detail'),
    path('periods/<uuid:uuid>/close/', AccountingPeriodCloseView.as_view(), name='accountingperiod_close'),
]
