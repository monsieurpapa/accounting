from django import forms
from .models import FixedAsset

class FixedAssetForm(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = [
            'asset_code', 'name', 'description',
            'acquisition_date', 'acquisition_cost', 'salvage_value',
            'asset_account', 'accumulated_depreciation_account',
            'depreciation_expense_account', 'depreciation_method',
            'useful_life_years', 'status',
        ]
        widgets = {
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
