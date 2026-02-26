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
    AccountingPeriodListView, AccountingPeriodCreateView, AccountingPeriodUpdateView, AccountingPeriodDeleteView, AccountingPeriodDetailView
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
    path('accounts/<int:pk>/edit/', ChartOfAccountsUpdateView.as_view(), name='chart_of_accounts_edit'),
    path('accounts/<int:pk>/delete/', ChartOfAccountsDeleteView.as_view(), name='chart_of_accounts_delete'),
    path('accounts/<int:pk>/', ChartOfAccountsDetailView.as_view(), name='chart_of_accounts_detail'),
    path('journals/list/', JournalListView.as_view(), name='journal_list'),
    path('journals/create/', JournalCreateView.as_view(), name='journal_create'),
    path('journals/<int:pk>/edit/', JournalUpdateView.as_view(), name='journal_edit'),
    path('journals/<int:pk>/delete/', JournalDeleteView.as_view(), name='journal_delete'),
    path('journals/<int:pk>/', JournalDetailView.as_view(), name='journal_detail'),
    path('journal-entry/list/', JournalEntryListView.as_view(), name='journal_entry_list'),
    path('journal-entry/create/', JournalEntryCreateView.as_view(), name='journal_entry_create_cbv'),
    path('journal-entry/<int:pk>/edit/', JournalEntryUpdateView.as_view(), name='journal_entry_edit'),
    path('journal-entry/<int:pk>/delete/', JournalEntryDeleteView.as_view(), name='journal_entry_delete'),
    path('journal-entry/<int:pk>/', JournalEntryDetailView.as_view(), name='journal_entry_detail'),
    path('journal-entry/<int:pk>/post/', JournalEntryPostView.as_view(), name='journal_entry_post'),
    path('fiscalyears/', FiscalYearListView.as_view(), name='fiscalyear_list'),
    path('fiscalyears/create/', FiscalYearCreateView.as_view(), name='fiscalyear_create'),
    path('fiscalyears/<int:pk>/edit/', FiscalYearUpdateView.as_view(), name='fiscalyear_edit'),
    path('fiscalyears/<int:pk>/delete/', FiscalYearDeleteView.as_view(), name='fiscalyear_delete'),
    path('fiscalyears/<int:pk>/', FiscalYearDetailView.as_view(), name='fiscalyear_detail'),
    path('fiscalyear/<int:fiscal_year_id>/periods/', AccountingPeriodListView.as_view(), name='accountingperiod_list'),
    path('fiscalyear/<int:fiscal_year_id>/periods/create/', AccountingPeriodCreateView.as_view(), name='accountingperiod_create'),
    path('periods/<int:pk>/edit/', AccountingPeriodUpdateView.as_view(), name='accountingperiod_edit'),
    path('periods/<int:pk>/delete/', AccountingPeriodDeleteView.as_view(), name='accountingperiod_delete'),
    path('periods/<int:pk>/', AccountingPeriodDetailView.as_view(), name='accountingperiod_detail'),
]
