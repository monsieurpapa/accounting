from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('budgets/', views.budget_list, name='budgets'),
]
