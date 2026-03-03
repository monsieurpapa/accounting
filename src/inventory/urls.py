from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'inventory'


@login_required
def inventory_dashboard(request):
    return render(request, 'inventory/index.html')


urlpatterns = [
    path('', inventory_dashboard, name='index'),
]
