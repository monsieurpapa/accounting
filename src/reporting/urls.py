from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('', views.reporting_index, name='index'),
    path('general-ledger/', views.general_ledger, name='general_ledger'),
    path('balance-sheet/', views.balance_sheet, name='balance_sheet'),
    path('income-statement/', views.income_statement, name='income_statement'),
    path('trial-balance/', views.trial_balance, name='trial_balance'),
]
