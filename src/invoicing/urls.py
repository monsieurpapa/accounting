from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

app_name = 'invoicing'


@login_required
def invoicing_dashboard(request):
    return render(request, 'invoicing/index.html')


urlpatterns = [
    path('', invoicing_dashboard, name='index'),
]
