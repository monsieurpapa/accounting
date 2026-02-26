from django import forms
from .models import Budget, BudgetLine

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'fiscal_year', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class BudgetLineForm(forms.ModelForm):
    class Meta:
        model = BudgetLine
        fields = ['account', 'period', 'allocated_amount']
