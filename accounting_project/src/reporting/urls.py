from django.urls import path
from .views import general_ledger, balance_sheet, income_statement
from accounting.views import trial_balance

app_name = 'reporting'

urlpatterns = [
    path('general-ledger/', general_ledger, name='general_ledger'),
    path('balance-sheet/', balance_sheet, name='balance_sheet'),
    path('income-statement/', income_statement, name='income_statement'),
    path('trial-balance/', trial_balance, name='trial_balance'),
]
