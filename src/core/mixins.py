from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class TenantAccessMixin(LoginRequiredMixin):
    """
    Ensures that the user can only access objects belonging to their organization.
    """
    organization_field = 'organization'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        organization = self.request.user.profile.organization
        filter_kwargs = {self.organization_field: organization}
        return queryset.filter(**filter_kwargs)

    def form_valid(self, form):
        """Automatically assign the user's organization to the object."""
        form.instance.organization = self.request.user.profile.organization
        return super().form_valid(form)

class RoleRequiredMixin(TenantAccessMixin):
    """
    Ensures that the user has a specific role to access the view.
    """
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user_role = request.user.profile.role
        if user_role and user_role.name in self.required_roles:
            return super().dispatch(request, *args, **kwargs)
        
        raise PermissionDenied("You do not have the required role to access this page.")
