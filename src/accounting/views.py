from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import ChartOfAccounts, JournalEntry, FiscalYear, AccountingPeriod, Journal
from organization.models import Organization
from .forms import ChartOfAccountsForm, JournalForm, JournalEntryForm, EntryLineFormSet, FiscalYearForm, AccountingPeriodForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator
from core.mixins import TenantAccessMixin, RoleRequiredMixin


def journals(request):
    return HttpResponse("Journals")

def journal_entries(request):
    return HttpResponse("Journal Entries")

@permission_required('accounting.add_journalentry', raise_exception=True)
@login_required
def journal_entry_create(request):
    """View for creating a new journal entry."""
    # Get user's organization
    organization = request.user.profile.organization
    
    # Get all accounts for this organization for the form
    accounts = ChartOfAccounts.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('code')
    
    if request.method == 'POST':
        # Process form submission
        # In a real implementation, this would validate and save the journal entry
        messages.success(request, 'Écriture comptable créée avec succès.')
        return redirect('journal_entries')
    
    context = {
        'accounts': accounts,
        'today': timezone.now().date(),
    }
    
    return render(request, 'accounting/journal_entry_form.html', context)

@permission_required('accounting.change_journalentry', raise_exception=True)
@login_required
def journal_entry_edit(request, uuid):
    # Placeholder for edit logic using uuid
    entry = get_object_or_404(JournalEntry, uuid=uuid, organization=request.user.profile.organization)
    pass

@permission_required('accounting.delete_journalentry', raise_exception=True)
@login_required
def journal_entry_delete(request, uuid):
    # Placeholder for delete logic using uuid
    entry = get_object_or_404(JournalEntry, uuid=uuid, organization=request.user.profile.organization)
    pass

def chart_of_accounts(request):
    return HttpResponse("Chart of Accounts")

def trial_balance(request):
    return HttpResponse("Trial Balance")

@login_required
def dashboard(request):
    """Dashboard view showing summary information and recent transactions."""
    # Get user's organization
    organization = request.user.profile.organization
    
    # Get current fiscal year and period
    current_fiscal_year = FiscalYear.objects.filter(
        organization=organization,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).first()
    
    current_period = None
    fiscal_year_progress = 0
    
    if current_fiscal_year:
        current_period = AccountingPeriod.objects.filter(
            fiscal_year=current_fiscal_year,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first()
        
        # Calculate fiscal year progress
        total_days = (current_fiscal_year.end_date - current_fiscal_year.start_date).days
        days_passed = (timezone.now().date() - current_fiscal_year.start_date).days
        fiscal_year_progress = min(100, int((days_passed / total_days) * 100))
    
    # Get recent journal entries
    recent_entries = JournalEntry.objects.filter(
        organization=organization
    ).order_by('-date')[:5]
    
    # Calculate financial summaries
    # In a real implementation, these would be calculated from actual data
    cash_balance = 4600000  # Example value
    
    # Calculate monthly revenue and expenses
    first_day_of_month = timezone.now().date().replace(day=1)
    monthly_revenue = 11700000  # Example value
    monthly_expenses = 7300000  # Example value
    
    # Count pending entries
    pending_entries = JournalEntry.objects.filter(
        organization=organization,
        posted=False
    ).count()
    
    context = {
        'cash_balance': cash_balance,
        'monthly_revenue': monthly_revenue,
        'monthly_expenses': monthly_expenses,
        'pending_entries': pending_entries,
        'recent_entries': recent_entries,
        'current_fiscal_year': current_fiscal_year,
        'current_period': current_period,
        'fiscal_year_progress': fiscal_year_progress,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def chart_of_accounts(request):
    """View for displaying the chart of accounts."""
    # Get user's organization
    organization = request.user.profile.organization
    
    # Get all accounts for this organization
    accounts = ChartOfAccounts.objects.filter(
        organization=organization
    ).order_by('code')
    
    context = {
        'accounts': accounts,
    }
    
    return render(request, 'accounting/chart_of_accounts.html', context)

@login_required
def journal_entries(request):
    """View for displaying journal entries list."""
    # Get user's organization
    organization = request.user.profile.organization
    
    # Get all journal entries for this organization
    entries = JournalEntry.objects.filter(
        organization=organization
    ).order_by('-date', '-id')
    
    context = {
        'entries': entries,
    }
    
    return render(request, 'accounting/journal_entries.html', context)

@login_required
def trial_balance(request):
    """View for displaying the trial balance report."""
    # Get user's organization
    organization = request.user.profile.organization
    
    # Get fiscal years for the form
    fiscal_years = FiscalYear.objects.filter(
        organization=organization
    ).order_by('-start_date')
    
    # Get current fiscal year
    current_fiscal_year = fiscal_years.first()
    
    # Get periods for the current fiscal year
    periods = []
    if current_fiscal_year:
        periods = AccountingPeriod.objects.filter(
            fiscal_year=current_fiscal_year
        ).order_by('start_date')
    
    context = {
        'fiscal_years': fiscal_years,
        'current_fiscal_year': current_fiscal_year,
        'periods': periods,
        'generation_date': timezone.now().date(),
    }
    
    return render(request, 'reporting/trial_balance.html', context)

class ChartOfAccountsListView(TenantAccessMixin, ListView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts.html'
    context_object_name = 'accounts'

class ChartOfAccountsCreateView(TenantAccessMixin, CreateView):
    model = ChartOfAccounts
    form_class = ChartOfAccountsForm
    template_name = 'accounting/chart_of_accounts_form.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')

class ChartOfAccountsUpdateView(TenantAccessMixin, UpdateView):
    model = ChartOfAccounts
    form_class = ChartOfAccountsForm
    template_name = 'accounting/chart_of_accounts_form.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class ChartOfAccountsDeleteView(TenantAccessMixin, DeleteView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_confirm_delete.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class ChartOfAccountsDetailView(TenantAccessMixin, DetailView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_detail.html'
    context_object_name = 'account'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class JournalListView(TenantAccessMixin, ListView):
    model = Journal
    template_name = 'accounting/journal_list.html'
    context_object_name = 'journals'

class JournalCreateView(TenantAccessMixin, CreateView):
    model = Journal
    form_class = JournalForm
    template_name = 'accounting/journal_form.html'
    success_url = reverse_lazy('accounting:journal_list')

class JournalUpdateView(TenantAccessMixin, UpdateView):
    model = Journal
    form_class = JournalForm
    template_name = 'accounting/journal_form.html'
    success_url = reverse_lazy('accounting:journal_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class JournalDeleteView(TenantAccessMixin, DeleteView):
    model = Journal
    template_name = 'accounting/journal_confirm_delete.html'
    success_url = reverse_lazy('accounting:journal_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class JournalDetailView(TenantAccessMixin, DetailView):
    model = Journal
    template_name = 'accounting/journal_detail.html'
    context_object_name = 'journal'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class JournalEntryListView(TenantAccessMixin, ListView):
    model = JournalEntry
    template_name = 'accounting/journal_entries.html'
    context_object_name = 'journal_entries'

class JournalEntryCreateView(TenantAccessMixin, CreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'accounting/journal_entry_form.html'
    success_url = reverse_lazy('accounting:journal_entry_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = EntryLineFormSet(self.request.POST)
        else:
            context['formset'] = EntryLineFormSet()
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        # form.instance.organization set by TenantAccessMixin
        form.instance.created_by = self.request.user
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        return self.form_invalid(form)

class JournalEntryUpdateView(TenantAccessMixin, UpdateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'accounting/journal_entry_form.html'
    success_url = reverse_lazy('accounting:journal_entry_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    def get_queryset(self):
        return super().get_queryset().filter(posted=False)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = EntryLineFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = EntryLineFormSet(instance=self.object)
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        return self.form_invalid(form)

class JournalEntryDeleteView(TenantAccessMixin, DeleteView):
    model = JournalEntry
    template_name = 'accounting/journal_entry_confirm_delete.html'
    success_url = reverse_lazy('accounting:journal_entry_list')
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class JournalEntryDetailView(TenantAccessMixin, DetailView):
    model = JournalEntry
    template_name = 'accounting/journal_entry_detail.html'
    context_object_name = 'entry'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class JournalEntryPostView(RoleRequiredMixin, TenantAccessMixin, UpdateView):
    model = JournalEntry
    fields = []
    template_name = 'accounting/journal_entry_post_confirm.html'
    success_url = reverse_lazy('accounting:journal_entry_list')
    required_roles = ['Senior Accountant', 'Admin']
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_queryset(self):
        return super().get_queryset().filter(posted=False)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.posted:
            messages.warning(request, 'Entry already posted.')
            return redirect('accounting:journal_entry_detail', uuid=self.object.uuid)
        
        # US 1.1: Prevent posting unbalanced entries
        if not self.object.lines.exists():
            messages.error(request, 'Cannot post an entry with no lines.')
            return redirect('accounting:journal_entry_detail', uuid=self.object.uuid)
            
        if not self.object.is_balanced:
            messages.error(request, f'Cannot post unbalanced entry. Total Debit: {self.object.total_debit}, Total Credit: {self.object.total_credit}')
            return redirect('accounting:journal_entry_detail', uuid=self.object.uuid)

        self.object.posted = True
        self.object.posted_by = request.user
        self.object.save()
        messages.success(request, 'Entry posted successfully.')
        return redirect(self.success_url)

class FiscalYearListView(TenantAccessMixin, ListView):
    model = FiscalYear
    template_name = 'accounting/fiscalyear_list.html'
    context_object_name = 'fiscalyears'

class FiscalYearCreateView(RoleRequiredMixin, TenantAccessMixin, CreateView):
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'accounting/fiscalyear_form.html'
    success_url = reverse_lazy('accounting:fiscalyear_list')
    required_roles = ['Admin']

class FiscalYearUpdateView(RoleRequiredMixin, TenantAccessMixin, UpdateView):
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'accounting/fiscalyear_form.html'
    success_url = reverse_lazy('accounting:fiscalyear_list')
    required_roles = ['Admin']
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class FiscalYearDeleteView(RoleRequiredMixin, TenantAccessMixin, DeleteView):
    model = FiscalYear
    template_name = 'accounting/fiscalyear_confirm_delete.html'
    success_url = reverse_lazy('accounting:fiscalyear_list')
    required_roles = ['Admin']
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    def get_queryset(self):
        return FiscalYear.objects.filter(organization=self.request.user.profile.organization)

class FiscalYearDetailView(TenantAccessMixin, DetailView):
    model = FiscalYear
    template_name = 'accounting/fiscalyear_detail.html'
    context_object_name = 'fiscalyear'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class AccountingPeriodListView(TenantAccessMixin, ListView):
    model = AccountingPeriod
    template_name = 'accounting/accountingperiod_list.html'
    context_object_name = 'periods'
    def get_queryset(self):
        # We now use the UUID of the fiscal year in the URL
        fiscal_year_uuid = self.kwargs.get('uuid')
        return super().get_queryset().filter(fiscal_year__uuid=fiscal_year_uuid)

class AccountingPeriodCreateView(RoleRequiredMixin, TenantAccessMixin, CreateView):
    model = AccountingPeriod
    form_class = AccountingPeriodForm
    template_name = 'accounting/accountingperiod_form.html'
    required_roles = ['Admin']
    def get_success_url(self):
        return reverse_lazy('accounting:accountingperiod_list', kwargs={'uuid': self.kwargs['uuid']})
    def form_valid(self, form):
        fiscal_year = get_object_or_404(FiscalYear, uuid=self.kwargs['uuid'], organization=self.request.user.profile.organization)
        form.instance.fiscal_year = fiscal_year
        return super().form_valid(form)

class AccountingPeriodUpdateView(RoleRequiredMixin, TenantAccessMixin, UpdateView):
    model = AccountingPeriod
    form_class = AccountingPeriodForm
    template_name = 'accounting/accountingperiod_form.html'
    required_roles = ['Admin']
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    def get_success_url(self):
        return reverse_lazy('accounting:accountingperiod_list', kwargs={'uuid': self.object.fiscal_year.uuid})

class AccountingPeriodDeleteView(RoleRequiredMixin, TenantAccessMixin, DeleteView):
    model = AccountingPeriod
    template_name = 'accounting/accountingperiod_confirm_delete.html'
    required_roles = ['Admin']
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    def get_success_url(self):
        return reverse_lazy('accounting:accountingperiod_list', kwargs={'uuid': self.object.fiscal_year.uuid})

class AccountingPeriodDetailView(TenantAccessMixin, DetailView):
    model = AccountingPeriod
    template_name = 'accounting/accountingperiod_detail.html'
    context_object_name = 'period'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

class AccountingPeriodCloseView(TenantAccessMixin, DetailView):
    model = AccountingPeriod
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success, message = self.object.close_period()
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('accounting:accountingperiod_detail', uuid=self.object.uuid)
