from django import forms
from django.forms import inlineformset_factory
from .models import ChartOfAccounts, Journal, JournalEntry, EntryLine, FiscalYear, AccountingPeriod

class ChartOfAccountsForm(forms.ModelForm):
    class Meta:
        model = ChartOfAccounts
        exclude = ['organization']

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        exclude = ['organization']

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        exclude = ['organization', 'created_by', 'created_at', 'updated_at', 'sync_status']

class FiscalYearForm(forms.ModelForm):
    class Meta:
        model = FiscalYear
        exclude = ['organization']

class AccountingPeriodForm(forms.ModelForm):
    class Meta:
        model = AccountingPeriod
        exclude = ['fiscal_year']

EntryLineFormSet = inlineformset_factory(
    JournalEntry, EntryLine,
    fields=['account', 'debit_amount', 'credit_amount', 'description'],
    extra=2,
    can_delete=True
) 