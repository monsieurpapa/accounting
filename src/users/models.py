# /home/ubuntu/accounting_project/src/users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

# Import Organization model using app label syntax to avoid circular imports initially
# Proper import will be from organization.models import Organization

class Role(models.Model):
    """Defines user roles within the application."""
    name = models.CharField(_("Role Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    # Permissions can be linked via Django's built-in permission system or a ManyToManyField here
    # from django.contrib.auth.models import Permission
    # permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        app_label = 'users'

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Extends the default Django User model with organization and role."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    # Use string reference for ForeignKey to avoid direct import issues during initial setup
    organization = models.ForeignKey("organization.Organization", on_delete=models.PROTECT, related_name="user_profiles", verbose_name=_("Organization"))
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="user_profiles", verbose_name=_("Role"), null=True, blank=True)
    # Add other profile fields if needed (e.g., phone number)

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        app_label = 'users'

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from organization.models import Organization
        org = Organization.objects.first()
        if org is None:
            org = Organization.objects.create(name='Default Organization')
        UserProfile.objects.create(user=instance, organization=org)

