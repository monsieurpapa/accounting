from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from accounting.models import ChartOfAccounts, JournalEntry, EntryLine, FiscalYear, AccountingPeriod
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal

from core.mixins import _get_user_organization

from .export_utils import (
    export_pdf_general_ledger,
    export_excel_general_ledger,
    export_pdf_balance_sheet,
    export_excel_balance_sheet,
    export_pdf_income_statement,
    export_excel_income_statement,
    export_pdf_trial_balance,
    export_excel_trial_balance,
)


def _require_organization(request):
    """Return the user's organization or raise PermissionDenied if not set."""
    organization = _get_user_organization(request.user)
    if organization is None:
        raise PermissionDenied(
            "You are not assigned to an organization. Contact an administrator."
        )
    return organization


def _export_url(request, fmt):
    """Build a URL for exporting the current report.

    The resulting URL preserves all existing query parameters from the
    original request except any existing ``format`` parameter, which is
    replaced by ``fmt``.  This allows the templates to render a link that
    points back to the same view but with ``?format=pdf`` or ``?format=xlsx``
    appended.  If there are no query parameters other than ``format`` the
    returned string will still include the leading ``?`` so that it can be
    used directly in an ``href`` attribute.
    """

    # ``request.GET`` is a QueryDict which is immutable; make a copy so we
    # can modify it safely.
    params = request.GET.copy()
    # drop any pre‑existing format parameter to avoid duplicates
    params.pop('format', None)
    params['format'] = fmt
    query = params.urlencode()
    return f"{request.path}?{query}" if query else request.path


@login_required
def reporting_index(request):
    return render(request, 'reporting/index.html')

@login_required
def general_ledger(request):
    organization = _require_organization(request)
    accounts = ChartOfAccounts.objects.filter(organization=organization).order_by('code')
    fiscal_years = FiscalYear.objects.filter(organization=organization).order_by('-start_date')
    selected_account_id = request.GET.get('account')
    selected_fiscal_year_id = request.GET.get('fiscal_year')
    selected_period_id = request.GET.get('period')
    entry_lines = []
    selected_account = None
    periods = []
    fiscal_year = FiscalYear.objects.filter(pk=selected_fiscal_year_id, organization=organization).first() if selected_fiscal_year_id else None
    period = AccountingPeriod.objects.filter(pk=selected_period_id, fiscal_year__organization=organization).first() if selected_period_id else None
    if selected_fiscal_year_id and fiscal_year:
        periods = AccountingPeriod.objects.filter(fiscal_year=fiscal_year).order_by('start_date')
    if selected_account_id:
        selected_account = ChartOfAccounts.objects.filter(pk=selected_account_id, organization=organization).first()
        if selected_account:
            qs = EntryLine.objects.filter(account=selected_account, journal_entry__posted=True)
            if period:
                qs = qs.filter(journal_entry__date__gte=period.start_date, journal_entry__date__lte=period.end_date)
            elif fiscal_year:
                qs = qs.filter(journal_entry__date__gte=fiscal_year.start_date, journal_entry__date__lte=fiscal_year.end_date)
            entry_lines = qs.select_related('journal_entry').order_by('journal_entry__date', 'id')
    # Export formats (PDF/Excel)
    export_format = request.GET.get('format')
    if export_format == 'pdf' and selected_account:
        content = export_pdf_general_ledger(
            entry_lines, selected_account, timezone.now().date(),
            fiscal_year=fiscal_year if selected_fiscal_year_id else None,
            period=period if selected_period_id else None
        )
        resp = HttpResponse(content, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="general_ledger.pdf"'
        return resp
    if export_format == 'xlsx' and selected_account:
        content = export_excel_general_ledger(
            entry_lines, selected_account, timezone.now().date(),
            fiscal_year=fiscal_year if selected_fiscal_year_id else None,
            period=period if selected_period_id else None
        )
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="general_ledger.xlsx"'
        return resp

    context = {
        'accounts': accounts,
        'fiscal_years': fiscal_years,
        'periods': periods,
        'selected_account': selected_account,
        'entry_lines': entry_lines,
        'generation_date': timezone.now().date(),
        'export_pdf_url': _export_url(request, 'pdf'),
        'export_excel_url': _export_url(request, 'xlsx'),
    }
    return render(request, 'reporting/general_ledger.html', context)

@login_required
def balance_sheet(request):
    organization = _require_organization(request)
    as_of_date = request.GET.get('date', timezone.now().date())
    if isinstance(as_of_date, str):
        from datetime import datetime
        as_of_date = datetime.strptime(as_of_date, '%Y-%m-%d').date()

    from django.db.models import Sum, Q

    # Query accounts and aggregate posted entry lines
    accounts = ChartOfAccounts.objects.filter(
        organization=organization,
        account_type__in=['ASSET', 'LIABILITY', 'EQUITY']
    ).annotate(
        total_debit=Sum('entry_lines__debit_amount', filter=Q(entry_lines__journal_entry__posted=True, entry_lines__journal_entry__date__lte=as_of_date)),
        total_credit=Sum('entry_lines__credit_amount', filter=Q(entry_lines__journal_entry__posted=True, entry_lines__journal_entry__date__lte=as_of_date))
    )

    asset_accounts = []
    liability_accounts = []
    equity_accounts = []
    
    total_assets = Decimal("0.00")
    total_liabilities = Decimal("0.00")
    total_equity = Decimal("0.00")

    for acc in accounts:
        debit = acc.total_debit or Decimal("0.00")
        credit = acc.total_credit or Decimal("0.00")
        
        if acc.account_type == 'ASSET':
            balance = debit - credit
            if balance != 0:
                asset_accounts.append({'code': acc.code, 'name': acc.name, 'balance': balance})
                total_assets += balance
        elif acc.account_type == 'LIABILITY':
            balance = credit - debit
            if balance != 0:
                liability_accounts.append({'code': acc.code, 'name': acc.name, 'balance': balance})
                total_liabilities += balance
        elif acc.account_type == 'EQUITY':
            balance = credit - debit
            if balance != 0:
                equity_accounts.append({'code': acc.code, 'name': acc.name, 'balance': balance})
                total_equity += balance

    fiscal_years = FiscalYear.objects.filter(organization=organization).order_by('-start_date')
    current_fiscal_year = FiscalYear.objects.filter(
        organization=organization,
        start_date__lte=as_of_date,
        end_date__gte=as_of_date
    ).first()

    # Export formats (PDF/Excel)
    export_format = request.GET.get('format')
    if export_format == 'pdf':
        content = export_pdf_balance_sheet(
            asset_accounts, liability_accounts, equity_accounts,
            total_assets, total_liabilities, total_equity,
            as_of_date, timezone.now().date()
        )
        resp = HttpResponse(content, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="balance_sheet.pdf"'
        return resp
    if export_format == 'xlsx':
        content = export_excel_balance_sheet(
            asset_accounts, liability_accounts, equity_accounts,
            total_assets, total_liabilities, total_equity,
            as_of_date, timezone.now().date()
        )
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="balance_sheet.xlsx"'
        return resp

    context = {
        'as_of_date': as_of_date,
        'assets': asset_accounts,
        'liabilities': liability_accounts,
        'equity': equity_accounts,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'generation_date': timezone.now().date(),
        'fiscal_years': fiscal_years,
        'current_fiscal_year': current_fiscal_year,
        'export_pdf_url': _export_url(request, 'pdf'),
        'export_excel_url': _export_url(request, 'xlsx'),
    }
    return render(request, 'reporting/balance_sheet.html', context)

@login_required
def income_statement(request):
    organization = _require_organization(request)
    fiscal_year_id = request.GET.get('fiscal_year')
    period_id = request.GET.get('period')
    
    start_date = None
    end_date = None
    fiscal_year = None
    period = None

    if period_id:
        period = AccountingPeriod.objects.filter(pk=period_id, fiscal_year__organization=organization).first()
        if period:
            start_date = period.start_date
            end_date = period.end_date
    elif fiscal_year_id:
        fiscal_year = FiscalYear.objects.filter(pk=fiscal_year_id, organization=organization).first()
        if fiscal_year:
            start_date = fiscal_year.start_date
            end_date = fiscal_year.end_date
    else:
        # Default to current fiscal year
        fiscal_year = FiscalYear.objects.filter(
            organization=organization,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first()
        if fiscal_year:
            start_date = fiscal_year.start_date
            end_date = fiscal_year.end_date

    from django.db.models import Sum, Q

    revenue_accounts = []
    expense_accounts = []
    total_revenue = Decimal("0.00")
    total_expenses = Decimal("0.00")

    if start_date and end_date:
        accounts = ChartOfAccounts.objects.filter(
            organization=organization,
            account_type__in=['REVENUE', 'EXPENSE']
        ).annotate(
            total_debit=Sum('entry_lines__debit_amount', filter=Q(entry_lines__journal_entry__posted=True, entry_lines__journal_entry__date__gte=start_date, entry_lines__journal_entry__date__lte=end_date)),
            total_credit=Sum('entry_lines__credit_amount', filter=Q(entry_lines__journal_entry__posted=True, entry_lines__journal_entry__date__gte=start_date, entry_lines__journal_entry__date__lte=end_date))
        )

        for acc in accounts:
            debit = acc.total_debit or Decimal("0.00")
            credit = acc.total_credit or Decimal("0.00")
            
            if acc.account_type == 'REVENUE':
                balance = credit - debit
                if balance != 0:
                    revenue_accounts.append({'code': acc.code, 'name': acc.name, 'balance': balance})
                    total_revenue += balance
            elif acc.account_type == 'EXPENSE':
                balance = debit - credit
                if balance != 0:
                    expense_accounts.append({'code': acc.code, 'name': acc.name, 'balance': balance})
                    total_expenses += balance

    net_income = total_revenue - total_expenses

    fiscal_years = FiscalYear.objects.filter(organization=organization).order_by('-start_date')

    # Export formats (PDF/Excel)
    export_format = request.GET.get('format')
    if export_format == 'pdf' and start_date and end_date:
        content = export_pdf_income_statement(
            revenue_accounts, expense_accounts,
            total_revenue, total_expenses, net_income,
            start_date, end_date, timezone.now().date()
        )
        resp = HttpResponse(content, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="income_statement.pdf"'
        return resp
    if export_format == 'xlsx' and start_date and end_date:
        content = export_excel_income_statement(
            revenue_accounts, expense_accounts,
            total_revenue, total_expenses, net_income,
            start_date, end_date, timezone.now().date()
        )
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="income_statement.xlsx"'
        return resp

    context = {
        'fiscal_year': fiscal_year,
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'revenues': revenue_accounts,
        'expenses': expense_accounts,
        'total_revenue': total_revenue,
        'total_expense': total_expenses,
        'net_income': net_income,
        'generation_date': timezone.now().date(),
        'fiscal_years': fiscal_years,
        'current_fiscal_year': fiscal_year,
        'export_pdf_url': _export_url(request, 'pdf'),
        'export_excel_url': _export_url(request, 'xlsx'),
    }
    return render(request, 'reporting/income_statement.html', context)

@login_required
def trial_balance(request):
    organization = _require_organization(request)
    fiscal_year_id = request.GET.get('fiscal_year')
    period_id = request.GET.get('period')
    
    fiscal_year = None
    period = None
    start_date = None
    end_date = None

    if period_id:
        period = AccountingPeriod.objects.filter(pk=period_id, fiscal_year__organization=organization).first()
        if period:
            fiscal_year = period.fiscal_year
            start_date = period.start_date
            end_date = period.end_date
    elif fiscal_year_id:
        fiscal_year = FiscalYear.objects.filter(pk=fiscal_year_id, organization=organization).first()
        if fiscal_year:
            start_date = fiscal_year.start_date
            end_date = fiscal_year.end_date

    # Get all accounts
    accounts_qs = ChartOfAccounts.objects.filter(organization=organization).order_by('code')
    
    report_data = []
    grand_total_opening_debit = Decimal("0.00")
    grand_total_opening_credit = Decimal("0.00")
    grand_total_period_debit = Decimal("0.00")
    grand_total_period_credit = Decimal("0.00")
    grand_total_closing_debit = Decimal("0.00")
    grand_total_closing_credit = Decimal("0.00")

    if start_date and end_date:
        from django.db.models import Sum, Q
        
        for acc in accounts_qs:
            # Opening Balance (all posted entries before start_date)
            opening = EntryLine.objects.filter(
                account=acc,
                journal_entry__posted=True,
                journal_entry__date__lt=start_date
            ).aggregate(
                debit=Sum('debit_amount'),
                credit=Sum('credit_amount')
            )
            opening_debit = opening['debit'] or Decimal("0.00")
            opening_credit = opening['credit'] or Decimal("0.00")
            
            # Period Movement (all posted entries between start_date and end_date)
            period_move = EntryLine.objects.filter(
                account=acc,
                journal_entry__posted=True,
                journal_entry__date__gte=start_date,
                journal_entry__date__lte=end_date
            ).aggregate(
                debit=Sum('debit_amount'),
                credit=Sum('credit_amount')
            )
            period_debit = period_move['debit'] or Decimal("0.00")
            period_credit = period_move['credit'] or Decimal("0.00")
            
            # Closing Balance
            total_debit = opening_debit + period_debit
            total_credit = opening_credit + period_credit
            
            closing_debit = Decimal("0.00")
            closing_credit = Decimal("0.00")
            
            # Balance calculation
            net_balance = total_debit - total_credit
            if net_balance > 0:
                closing_debit = net_balance
            elif net_balance < 0:
                closing_credit = -net_balance
                
            report_data.append({
                'id': acc.id,
                'code': acc.code,
                'name': acc.name,
                'opening_debit': opening_debit,
                'opening_credit': opening_credit,
                'period_debit': period_debit,
                'period_credit': period_credit,
                'closing_debit': closing_debit,
                'closing_credit': closing_credit,
            })
            
            grand_total_opening_debit += opening_debit
            grand_total_opening_credit += opening_credit
            grand_total_period_debit += period_debit
            grand_total_period_credit += period_credit
            grand_total_closing_debit += closing_debit
            grand_total_closing_credit += closing_credit

    fiscal_years = FiscalYear.objects.filter(organization=organization).order_by('-start_date')

    # Export formats (PDF/Excel)
    export_format = request.GET.get('format')
    if export_format == 'pdf' and start_date and end_date:
        content = export_pdf_trial_balance(
            report_data,
            {'opening_debit': grand_total_opening_debit, 'opening_credit': grand_total_opening_credit,
             'period_debit': grand_total_period_debit, 'period_credit': grand_total_period_credit,
             'closing_debit': grand_total_closing_debit, 'closing_credit': grand_total_closing_credit},
            fiscal_year, period, start_date, end_date, timezone.now().date()
        )
        resp = HttpResponse(content, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="trial_balance.pdf"'
        return resp
    if export_format == 'xlsx' and start_date and end_date:
        content = export_excel_trial_balance(
            report_data,
            {'opening_debit': grand_total_opening_debit, 'opening_credit': grand_total_opening_credit,
             'period_debit': grand_total_period_debit, 'period_credit': grand_total_period_credit,
             'closing_debit': grand_total_closing_debit, 'closing_credit': grand_total_closing_credit},
            fiscal_year, period, start_date, end_date, timezone.now().date()
        )
        resp = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="trial_balance.xlsx"'
        return resp

    periods = AccountingPeriod.objects.filter(fiscal_year=fiscal_year).order_by('start_date') if fiscal_year else []

    context = {
        'fiscal_year': fiscal_year,
        'period': period,
        'periods': periods,
        'report_data': report_data,
        'grand_totals': {
            'opening_debit': grand_total_opening_debit,
            'opening_credit': grand_total_opening_credit,
            'period_debit': grand_total_period_debit,
            'period_credit': grand_total_period_credit,
            'closing_debit': grand_total_closing_debit,
            'closing_credit': grand_total_closing_credit,
        },
        'fiscal_years': fiscal_years,
        'generation_date': timezone.now().date(),
        'export_pdf_url': _export_url(request, 'pdf'),
        'export_excel_url': _export_url(request, 'xlsx'),
    }
    return render(request, 'reporting/trial_balance.html', context)
