from django import forms
from .models import Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'address', 'contact_info', 'unique_code', 'is_active']
