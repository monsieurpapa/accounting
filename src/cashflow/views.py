from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import ThirdParty, Payment, Receipt, BankReconciliation
from .forms import ThirdPartyForm, PaymentForm, ReceiptForm, BankReconciliationForm
from core.mixins import TenantAccessMixin, RoleRequiredMixin

class ThirdPartyListView(TenantAccessMixin, ListView):
    model = ThirdParty
    template_name = 'cashflow/thirdparty_list.html'
    context_object_name = 'third_parties'

class ThirdPartyCreateView(TenantAccessMixin, CreateView):
    model = ThirdParty
    form_class = ThirdPartyForm
    template_name = 'cashflow/thirdparty_form.html'
    success_url = reverse_lazy('cashflow:thirdparty_list')

class ThirdPartyUpdateView(TenantAccessMixin, UpdateView):
    model = ThirdParty
    form_class = ThirdPartyForm
    template_name = 'cashflow/thirdparty_form.html'
    success_url = reverse_lazy('cashflow:thirdparty_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class ThirdPartyDeleteView(TenantAccessMixin, DeleteView):
    model = ThirdParty
    template_name = 'cashflow/thirdparty_confirm_delete.html'
    success_url = reverse_lazy('cashflow:thirdparty_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class PaymentListView(TenantAccessMixin, ListView):
    model = Payment
    template_name = 'cashflow/payment_list.html'
    context_object_name = 'payments'

class PaymentCreateView(TenantAccessMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'cashflow/payment_form.html'
    success_url = reverse_lazy('cashflow:payment_list')

class ReceiptListView(TenantAccessMixin, ListView):
    model = Receipt
    template_name = 'cashflow/receipt_list.html'
    context_object_name = 'receipts'

class ReceiptCreateView(TenantAccessMixin, CreateView):
    model = Receipt
    form_class = ReceiptForm
    template_name = 'cashflow/receipt_form.html'
    success_url = reverse_lazy('cashflow:receipt_list')

class BankReconciliationListView(TenantAccessMixin, ListView):
    model = BankReconciliation
    template_name = 'cashflow/bankreconciliation_list.html'
    context_object_name = 'reconciliations'

class BankReconciliationCreateView(RoleRequiredMixin, CreateView):
    model = BankReconciliation
    form_class = BankReconciliationForm
    template_name = 'cashflow/bankreconciliation_form.html'
    success_url = reverse_lazy('cashflow:bankreconciliation_list')
    role_required = 'Senior Accountant'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.calculate_balances()
        self.object.save()
        return response

class BankReconciliationDetailView(TenantAccessMixin, DetailView):
    model = BankReconciliation
    template_name = 'cashflow/bankreconciliation_detail.html'
    context_object_name = 'reconciliation'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounting.models import EntryLine
        # Show uncleared items for this account up to statement date
        context['uncleared_items'] = EntryLine.objects.filter(
            account=self.object.bank_account,
            journal_entry__posted=True,
            journal_entry__date__lte=self.object.statement_date,
            is_cleared=False
        )
        return context

class BankReconciliationReconcileView(TenantAccessMixin, DetailView):
    model = BankReconciliation
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.reconcile(request.user):
            messages.success(request, _("Bank reconciliation successfully finalized."))
        else:
            messages.error(request, _("Cannot reconcile. Differences still exist."))
        return redirect('cashflow:bankreconciliation_detail', uuid=self.object.uuid)
