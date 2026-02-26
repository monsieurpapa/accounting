# /home/ubuntu/accounting_project/src/organization/models.py
from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _

class Organization(models.Model):
    """Represents a hospital or site."""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(_("Name"), max_length=255, unique=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    contact_info = models.TextField(_("Contact Information"), blank=True, null=True)
    unique_code = models.CharField(_("Unique Code"), max_length=50, unique=True, blank=True, null=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        app_label = 'organization' # Explicitly set app_label

    def __str__(self):
        return self.name

