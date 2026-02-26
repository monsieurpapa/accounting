from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Budget, BudgetLine, BudgetCommitment
from .forms import BudgetForm, BudgetLineForm
from core.mixins import TenantAccessMixin, RoleRequiredMixin

class BudgetListView(TenantAccessMixin, ListView):
    model = Budget
    template_name = 'budget/budget_list.html'
    context_object_name = 'budgets'

class BudgetCreateView(TenantAccessMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('budget:budget_list')

class BudgetUpdateView(TenantAccessMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'budget/budget_form.html'
    success_url = reverse_lazy('budget:budget_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class BudgetDeleteView(TenantAccessMixin, DeleteView):
    model = Budget
    template_name = 'budget/budget_confirm_delete.html'
    success_url = reverse_lazy('budget:budget_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class BudgetDetailView(TenantAccessMixin, DetailView):
    model = Budget
    template_name = 'budget/budget_detail.html'
    context_object_name = 'budget'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class BudgetLineCreateView(TenantAccessMixin, CreateView):
    model = BudgetLine
    form_class = BudgetLineForm
    template_name = 'budget/budgetline_form.html'

    def get_success_url(self):
        return reverse_lazy('budget:budget_detail', kwargs={'uuid': self.kwargs['budget_uuid']})

    def form_valid(self, form):
        budget = get_object_or_404(Budget, uuid=self.kwargs['budget_uuid'], organization=self.request.user.profile.organization)
        form.instance.budget = budget
        return super().form_valid(form)

class BudgetLineUpdateView(TenantAccessMixin, UpdateView):
    model = BudgetLine
    form_class = BudgetLineForm
    template_name = 'budget/budgetline_form.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self):
        return reverse_lazy('budget:budget_detail', kwargs={'uuid': self.object.budget.uuid})

class BudgetLineDeleteView(TenantAccessMixin, DeleteView):
    model = BudgetLine
    template_name = 'budget/budgetline_confirm_delete.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self):
        return reverse_lazy('budget:budget_detail', kwargs={'uuid': self.object.budget.uuid})
