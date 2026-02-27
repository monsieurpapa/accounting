"""
URL configuration for the Accounting System.

Root routing: admin, allauth, i18n, budget, reporting, users,
organization, cashflow, and accounting (root namespace).
See docs/API.md for full URL reference.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('budget/', include(('budget.urls', 'budget'), namespace='budget')),
    path('reporting/', include(('reporting.urls', 'reporting'), namespace='reporting')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('organization/', include(('organization.urls', 'organization'), namespace='organization')),
    path('cashflow/', include(('cashflow.urls', 'cashflow'), namespace='cashflow')),
    path('', include(('accounting.urls', 'accounting'), namespace='accounting')),

]
