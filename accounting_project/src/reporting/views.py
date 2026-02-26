from django.shortcuts import render
from accounting.models import ChartOfAccounts, JournalEntry, EntryLine, FiscalYear, AccountingPeriod
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal

@login_required
def general_ledger(request):
    organization = request.user.profile.organization
    accounts = ChartOfAccounts.objects.filter(organization=organization).order_by('code')
    fiscal_years = FiscalYear.objects.filter(organization=organization).order_by('-start_date')
    selected_account_id = request.GET.get('account')
    selected_fiscal_year_id = request.GET.get('fiscal_year')
    selected_period_id = request.GET.get('period')
    entry_lines = []
    selected_account = None
    periods = []
    if selected_fiscal_year_id:
        fiscal_year = FiscalYear.objects.filter(pk=selected_fiscal_year_id, organization=organization).first()
        if fiscal_year:
            periods = AccountingPeriod.objects.filter(fiscal_year=fiscal_year).order_by('start_date')
    if selected_account_id:
        selected_account = ChartOfAccounts.objects.filter(pk=selected_account_id, organization=organization).first()
        if selected_account:
            qs = EntryLine.objects.filter(account=selected_account, journal_entry__posted=True)
            if selected_period_id:
                period = AccountingPeriod.objects.filter(pk=selected_period_id, fiscal_year__organization=organization).first()
                if period:
                    qs = qs.filter(journal_entry__date__gte=period.start_date, journal_entry__date__lte=period.end_date)
            elif selected_fiscal_year_id and fiscal_year:
                qs = qs.filter(journal_entry__date__gte=fiscal_year.start_date, journal_entry__date__lte=fiscal_year.end_date)
            entry_lines = qs.select_related('journal_entry').order_by('journal_entry__date', 'id')
    context = {
        'accounts': accounts,
        'fiscal_years': fiscal_years,
        'periods': periods,
        'selected_account': selected_account,
        'entry_lines': entry_lines,
        'generation_date': timezone.now().date(),
    }
    return render(request, 'reporting/general_ledger.html', context)

@login_required
def balance_sheet(request):
    # Stub: implement real calculation logic
    return render(request, 'reporting/balance_sheet.html', {'generation_date': timezone.now().date()})

@login_required
def income_statement(request):
    # Stub: implement real calculation logic
    return render(request, 'reporting/income_statement.html', {'generation_date': timezone.now().date()})
