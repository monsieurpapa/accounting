from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


def _get_user_organization(user):
    """
    Return the organization for the user, or None if not set.
    Handles missing profile or organization safely.
    """
    if not user.is_authenticated:
        return None
    if not hasattr(user, 'profile'):
        return None
    try:
        return user.profile.organization
    except Exception:
        return None


class TenantAccessMixin(LoginRequiredMixin):
    """
    Ensures that the user can only access objects belonging to their organization.
    Users without a profile or organization get an empty queryset and cannot create
    objects (PermissionDenied on form_valid if organization is missing).
    """
    organization_field = 'organization'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        organization = _get_user_organization(self.request.user)
        if organization is None:
            return queryset.none()
        filter_kwargs = {self.organization_field: organization}
        return queryset.filter(**filter_kwargs)

    def form_valid(self, form):
        """Automatically assign the user's organization to the object."""
        organization = _get_user_organization(self.request.user)
        if organization is None:
            raise PermissionDenied(
                "You are not assigned to an organization. Contact an administrator."
            )
        form.instance.organization = organization
        return super().form_valid(form)


class RoleRequiredMixin(TenantAccessMixin):
    """
    Restricts the view to users with one of the required roles.
    Staff and superusers bypass the role check and can access the view.
    Set required_roles on the view class, e.g. required_roles = ['Admin', 'Senior Accountant'].
    """
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # Staff and superuser can perform all role-restricted actions
        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        user_role = getattr(
            getattr(request.user, 'profile', None), 'role', None
        )
        if user_role and user_role.name in self.required_roles:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied(
            "You do not have the required role to access this page."
        )
