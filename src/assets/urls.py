from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('assets/', views.FixedAssetListView.as_view(), name='fixedasset_list'),
    path('assets/create/', views.FixedAssetCreateView.as_view(), name='fixedasset_create'),
    path('assets/<uuid:uuid>/', views.FixedAssetDetailView.as_view(), name='fixedasset_detail'),
    path('assets/<uuid:uuid>/edit/', views.FixedAssetUpdateView.as_view(), name='fixedasset_edit'),
    path('assets/<uuid:uuid>/delete/', views.FixedAssetDeleteView.as_view(), name='fixedasset_delete'),
]
