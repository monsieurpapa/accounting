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

def dashboard(request):
    return HttpResponse("Dashboard")

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
def journal_entry_edit(request, pk):
    # Placeholder for edit logic
    pass

@permission_required('accounting.delete_journalentry', raise_exception=True)
@login_required
def journal_entry_delete(request, pk):
    # Placeholder for delete logic
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

class ChartOfAccountsListView(ListView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_list.html'
    context_object_name = 'accounts'
    def get_queryset(self):
        return ChartOfAccounts.objects.filter(organization=self.request.user.profile.organization)

class ChartOfAccountsCreateView(CreateView):
    model = ChartOfAccounts
    form_class = ChartOfAccountsForm
    template_name = 'accounting/chart_of_accounts_form.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')
    def form_valid(self, form):
        form.instance.organization = self.request.user.profile.organization
        return super().form_valid(form)

class ChartOfAccountsUpdateView(UpdateView):
    model = ChartOfAccounts
    form_class = ChartOfAccountsForm
    template_name = 'accounting/chart_of_accounts_form.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')
    def get_queryset(self):
        return ChartOfAccounts.objects.filter(organization=self.request.user.profile.organization)

class ChartOfAccountsDeleteView(DeleteView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_confirm_delete.html'
    success_url = reverse_lazy('accounting:chart_of_accounts_list')
    def get_queryset(self):
        return ChartOfAccounts.objects.filter(organization=self.request.user.profile.organization)

class ChartOfAccountsDetailView(DetailView):
    model = ChartOfAccounts
    template_name = 'accounting/chart_of_accounts_detail.html'
    context_object_name = 'account'
    def get_queryset(self):
        return ChartOfAccounts.objects.filter(organization=self.request.user.profile.organization)

class JournalListView(ListView):
    model = Journal
    template_name = 'accounting/journal_list.html'
    context_object_name = 'journals'
    def get_queryset(self):
        return Journal.objects.filter(organization=self.request.user.profile.organization)

class JournalCreateView(CreateView):
    model = Journal
    form_class = JournalForm
    template_name = 'accounting/journal_form.html'
    success_url = reverse_lazy('accounting:journal_list')
    def form_valid(self, form):
        form.instance.organization = self.request.user.profile.organization
        return super().form_valid(form)

class JournalUpdateView(UpdateView):
    model = Journal
    form_class = JournalForm
    template_name = 'accounting/journal_form.html'
    success_url = reverse_lazy('accounting:journal_list')
    def get_queryset(self):
        return Journal.objects.filter(organization=self.request.user.profile.organization)

class JournalDeleteView(DeleteView):
    model = Journal
    template_name = 'accounting/journal_confirm_delete.html'
    success_url = reverse_lazy('accounting:journal_list')
    def get_queryset(self):
        return Journal.objects.filter(organization=self.request.user.profile.organization)

class JournalDetailView(DetailView):
    model = Journal
    template_name = 'accounting/journal_detail.html'
    context_object_name = 'journal'
    def get_queryset(self):
        return Journal.objects.filter(organization=self.request.user.profile.organization)

class JournalEntryListView(ListView):
    model = JournalEntry
    template_name = 'accounting/journal_entry_list.html'
    context_object_name = 'entries'
    def get_queryset(self):
        return JournalEntry.objects.filter(organization=self.request.user.profile.organization)

class JournalEntryCreateView(CreateView):
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
        form.instance.organization = self.request.user.profile.organization
        form.instance.created_by = self.request.user
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        return self.form_invalid(form)

class JournalEntryUpdateView(UpdateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'accounting/journal_entry_form.html'
    success_url = reverse_lazy('accounting:journal_entry_list')
    def get_queryset(self):
        return JournalEntry.objects.filter(organization=self.request.user.profile.organization, posted=False)
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

class JournalEntryDeleteView(DeleteView):
    model = JournalEntry
    template_name = 'accounting/journal_entry_confirm_delete.html'
    success_url = reverse_lazy('accounting:journal_entry_list')
    def get_queryset(self):
        return JournalEntry.objects.filter(organization=self.request.user.profile.organization)

class JournalEntryDetailView(DetailView):
    model = JournalEntry
    template_name = 'accounting/journal_entry_detail.html'
    context_object_name = 'entry'
    def get_queryset(self):
        return JournalEntry.objects.filter(organization=self.request.user.profile.organization)

@method_decorator(login_required, name='dispatch')
class JournalEntryPostView(UpdateView):
    model = JournalEntry
    fields = []
    template_name = 'accounting/journal_entry_post_confirm.html'
    success_url = reverse_lazy('accounting:journal_entry_list')
    def get_queryset(self):
        return JournalEntry.objects.filter(organization=self.request.user.profile.organization, posted=False)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.posted:
            messages.warning(request, 'Entry already posted.')
            return redirect('accounting:journal_entry_detail', pk=self.object.pk)
        self.object.posted = True
        self.object.save()
        messages.success(request, 'Entry posted successfully.')
        return redirect(self.success_url)

class FiscalYearListView(ListView):
    model = FiscalYear
    template_name = 'accounting/fiscalyear_list.html'
    context_object_name = 'fiscalyears'
    def get_queryset(self):
        return FiscalYear.objects.filter(organization=self.request.user.profile.organization)

@method_decorator(permission_required('accounting.add_fiscalyear', raise_exception=True), name='dispatch')
class FiscalYearCreateView(CreateView):
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'accounting/fiscalyear_form.html'
    success_url = reverse_lazy('accounting:fiscalyear_list')
    def form_valid(self, form):
        form.instance.organization = self.request.user.profile.organization
        return super().form_valid(form)

@method_decorator(permission_required('accounting.change_fiscalyear', raise_exception=True), name='dispatch')
class FiscalYearUpdateView(UpdateView):
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'accounting/fiscalyear_form.html'
    success_url = reverse_lazy('accounting:fiscalyear_list')
    def get_queryset(self):
        return FiscalYear.objects.filter(organization=self.request.user.profile.organization)

@method_decorator(permission_required('accounting.delete_fiscalyear', raise_exception=True), name='dispatch')
class FiscalYearDeleteView(DeleteView):
    model = FiscalYear
    template_name = 'accounting/fiscalyear_confirm_delete.html'
    success_url = reverse_lazy('accounting:fiscalyear_list')
    def get_queryset(self):
        return FiscalYear.objects.filter(organization=self.request.user.profile.organization)

class FiscalYearDetailView(DetailView):
    model = FiscalYear
    template_name = 'accounting/fiscalyear_detail.html'
    context_object_name = 'fiscalyear'
    def get_queryset(self):
        return FiscalYear.objects.filter(organization=self.request.user.profile.organization)

class AccountingPeriodListView(ListView):
    model = AccountingPeriod
    template_name = 'accounting/accountingperiod_list.html'
    context_object_name = 'periods'
    def get_queryset(self):
        fiscal_year_id = self.kwargs.get('fiscal_year_id')
        return AccountingPeriod.objects.filter(fiscal_year__organization=self.request.user.profile.organization, fiscal_year_id=fiscal_year_id)

@method_decorator(permission_required('accounting.add_accountingperiod', raise_exception=True), name='dispatch')
class AccountingPeriodCreateView(CreateView):
    model = AccountingPeriod
    form_class = AccountingPeriodForm
    template_name = 'accounting/accountingperiod_form.html'
    def get_success_url(self):
        return reverse_lazy('accounting:accountingperiod_list', kwargs={'fiscal_year_id': self.kwargs['fiscal_year_id']})
    def form_valid(self, form):
        fiscal_year = get_object_or_404(FiscalYear, pk=self.kwargs['fiscal_year_id'], organization=self.request.user.profile.organization)
        form.instance.fiscal_year = fiscal_year
        return super().form_valid(form)

@method_decorator(permission_required('accounting.change_accountingperiod', raise_exception=True), name='dispatch')
class AccountingPeriodUpdateView(UpdateView):
    model = AccountingPeriod
    form_class = AccountingPeriodForm
    template_name = 'accounting/accountingperiod_form.html'
    def get_success_url(self):
        return reverse_lazy('accounting:accountingperiod_list', kwargs={'fiscal_year_id': self.object.fiscal_year_id})
    def get_queryset(self):
        return AccountingPeriod.objects.filter(fiscal_year__organization=self.request.user.profile.organization)

@method_decorator(permission_required('accounting.delete_accountingperiod', raise_exception=True), name='dispatch')
class AccountingPeriodDeleteView(DeleteView):
    model = AccountingPeriod
    template_name = 'accounting/accountingperiod_confirm_delete.html'
    def get_success_url(self):
        return reverse_lazy('accounting:accountingperiod_list', kwargs={'fiscal_year_id': self.object.fiscal_year_id})
    def get_queryset(self):
        return AccountingPeriod.objects.filter(fiscal_year__organization=self.request.user.profile.organization)

class AccountingPeriodDetailView(DetailView):
    model = AccountingPeriod
    template_name = 'accounting/accountingperiod_detail.html'
    context_object_name = 'period'
    def get_queryset(self):
        return AccountingPeriod.objects.filter(fiscal_year__organization=self.request.user.profile.organization)
