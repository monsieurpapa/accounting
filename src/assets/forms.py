from django import forms
from .models import FixedAsset

class FixedAssetForm(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = [
            'asset_code', 'name', 'asset_account', 'accumulated_depreciation_account', 
            'depreciation_expense_account', 'acquisition_date', 
            'acquisition_cost', 'salvage_value', 'useful_life_years', 
            'depreciation_method', 'description'
        ]
