from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import FixedAsset, DepreciationMethod, DepreciationEntry
from .forms import FixedAssetForm
from core.mixins import TenantAccessMixin, RoleRequiredMixin

class FixedAssetListView(TenantAccessMixin, ListView):
    model = FixedAsset
    template_name = 'assets/fixedasset_list.html'
    context_object_name = 'assets'

class FixedAssetCreateView(TenantAccessMixin, CreateView):
    model = FixedAsset
    form_class = FixedAssetForm
    template_name = 'assets/fixedasset_form.html'
    success_url = reverse_lazy('assets:fixedasset_list')

class FixedAssetUpdateView(TenantAccessMixin, UpdateView):
    model = FixedAsset
    form_class = FixedAssetForm
    template_name = 'assets/fixedasset_form.html'
    success_url = reverse_lazy('assets:fixedasset_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class FixedAssetDeleteView(TenantAccessMixin, DeleteView):
    model = FixedAsset
    template_name = 'assets/fixedasset_confirm_delete.html'
    success_url = reverse_lazy('assets:fixedasset_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class FixedAssetDetailView(TenantAccessMixin, DetailView):
    model = FixedAsset
    template_name = 'assets/fixedasset_detail.html'
    context_object_name = 'asset'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
