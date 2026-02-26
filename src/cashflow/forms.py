from django import forms
from .models import ThirdParty, Payment, Receipt, BankReconciliation

class ThirdPartyForm(forms.ModelForm):
    class Meta:
        model = ThirdParty
        fields = ['name', 'type', 'contact_info', 'address', 'tax_id', 'receivable_account', 'payable_account', 'bank_account', 'is_active']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'third_party', 'amount', 'payment_method', 'reference', 'description']

class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['date', 'third_party', 'amount', 'payment_method', 'reference', 'description']

class BankReconciliationForm(forms.ModelForm):
    class Meta:
        model = BankReconciliation
        fields = ['bank_account', 'statement_date', 'statement_end_balance']
