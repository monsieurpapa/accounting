from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import UserAdminForm
from .models import Role
from organization.models import Organization

@login_required
def profile(request):
    return render(request, 'users/profile.html')


# ----------------------------------------------------------------------------
# Administrative user management (superuser only)
# ----------------------------------------------------------------------------

def _staff_required(request):
    # Require Django superuser for these admin actions
    if not request.user.is_superuser:
        raise PermissionDenied


@login_required
def user_list(request):
    """Show a simple list of all users."""
    _staff_required(request)
    users = User.objects.all().select_related('profile')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def user_create(request):
    _staff_required(request)
    if request.method == 'POST':
        form = UserAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:user_list')
    else:
        form = UserAdminForm()
    return render(request, 'users/user_form.html', {'form': form, 'creating': True})


@login_required
def user_update(request, pk):
    _staff_required(request)
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:user_list')
    else:
        # prepopulate organization and role from profile
        initial = {}
        if hasattr(user, 'profile'):
            initial['organization'] = user.profile.organization
            initial['role'] = user.profile.role
        form = UserAdminForm(instance=user, initial=initial)
    return render(request, 'users/user_form.html', {'form': form, 'creating': False})


@login_required
def user_delete(request, pk):
    _staff_required(request)
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})


@login_required
def user_detail(request, pk):
    """Show read-only details for a user (superuser only)."""
    _staff_required(request)
    user = get_object_or_404(User, pk=pk)
    profile = getattr(user, 'profile', None)
    return render(request, 'users/user_detail.html', {'user_obj': user, 'profile': profile})
