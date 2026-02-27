from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

from .models import Role, UserProfile
from organization.models import Organization


class UserAdminForm(forms.ModelForm):
    """Form used by admin views to create or edit users along with profile data."""
    password = forms.CharField(widget=forms.PasswordInput, required=False,
                               help_text="Leave blank to keep existing password.")
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password',
                  'is_staff', 'is_active']

    def save(self, commit=True):
        # override save to handle password hashing and profile fields
        user = super().save(commit=False)
        pw = self.cleaned_data.get('password')
        if pw:
            user.set_password(pw)
        if commit:
            user.save()
            # update or create profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.organization = self.cleaned_data['organization']
            profile.role = self.cleaned_data.get('role')
            profile.save()
        return user
