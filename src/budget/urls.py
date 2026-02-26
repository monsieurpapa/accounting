from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<uuid:uuid>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<uuid:uuid>/edit/', views.BudgetUpdateView.as_view(), name='budget_edit'),
    path('budgets/<uuid:uuid>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
    
    path('budgets/<uuid:budget_uuid>/lines/create/', views.BudgetLineCreateView.as_view(), name='budgetline_create'),
    path('lines/<uuid:uuid>/edit/', views.BudgetLineUpdateView.as_view(), name='budgetline_edit'),
    path('lines/<uuid:uuid>/delete/', views.BudgetLineDeleteView.as_view(), name='budgetline_delete'),
]
