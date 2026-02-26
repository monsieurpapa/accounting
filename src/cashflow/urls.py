from django.urls import path
from . import views

app_name = 'cashflow'

urlpatterns = [
    path('third-parties/', views.ThirdPartyListView.as_view(), name='thirdparty_list'),
    path('third-parties/create/', views.ThirdPartyCreateView.as_view(), name='thirdparty_create'),
    path('third-parties/<uuid:uuid>/edit/', views.ThirdPartyUpdateView.as_view(), name='thirdparty_edit'),
    path('third-parties/<uuid:uuid>/delete/', views.ThirdPartyDeleteView.as_view(), name='thirdparty_delete'),
    
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    
    path('receipts/', views.ReceiptListView.as_view(), name='receipt_list'),
    path('receipts/create/', views.ReceiptCreateView.as_view(), name='receipt_create'),
    
    path('reconciliations/', views.BankReconciliationListView.as_view(), name='bankreconciliation_list'),
    path('reconciliations/create/', views.BankReconciliationCreateView.as_view(), name='bankreconciliation_create'),
    path('reconciliations/<uuid:uuid>/', views.BankReconciliationDetailView.as_view(), name='bankreconciliation_detail'),
    path('reconciliations/<uuid:uuid>/reconcile/', views.BankReconciliationReconcileView.as_view(), name='bankreconciliation_reconcile'),
]
