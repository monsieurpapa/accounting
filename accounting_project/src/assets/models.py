# /home/ubuntu/accounting_project/src/assets/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Use string references for ForeignKey to avoid circular imports initially

class DepreciationMethod(models.Model):
    """Defines depreciation methods (e.g., Straight-line)."""
    name = models.CharField(_("Method Name"), max_length=100, unique=True)
    calculation_logic = models.TextField(_("Calculation Logic/Description"), blank=True, null=True)

    class Meta:
        verbose_name = _("Depreciation Method")
        verbose_name_plural = _("Depreciation Methods")
        app_label = 'assets'

    def __str__(self):
        return self.name

class FixedAsset(models.Model):
    """Represents a fixed asset."""
    STATUS_CHOICES = [
        ("ACTIVE", _("Active")),
        ("DISPOSED", _("Disposed")),
        ("SOLD", _("Sold")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="fixed_assets")
    asset_code = models.CharField(_("Asset Code"), max_length=50)
    name = models.CharField(_("Asset Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    acquisition_date = models.DateField(_("Acquisition Date"))
    acquisition_cost = models.DecimalField(_("Acquisition Cost"), max_digits=15, decimal_places=2)
    asset_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="asset_account_for", verbose_name=_("Asset Account"))
    accumulated_depreciation_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="accumulated_depreciation_for", verbose_name=_("Accumulated Depreciation Account"))
    depreciation_expense_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="depreciation_expense_for", verbose_name=_("Depreciation Expense Account"))
    depreciation_method = models.ForeignKey(DepreciationMethod, on_delete=models.PROTECT, verbose_name=_("Depreciation Method"))
    useful_life_years = models.PositiveIntegerField(_("Useful Life (Years)"))
    salvage_value = models.DecimalField(_("Salvage Value"), max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    disposal_date = models.DateField(_("Disposal Date"), null=True, blank=True)
    # Link to maintenance service if needed

    class Meta:
        verbose_name = _("Fixed Asset")
        verbose_name_plural = _("Fixed Assets")
        unique_together = [("organization", "asset_code")]
        ordering = ["acquisition_date"]
        app_label = 'assets'

    def __str__(self):
        return f"{self.asset_code} - {self.name}"

class DepreciationEntry(models.Model):
    """Records a single depreciation calculation entry."""
    asset = models.ForeignKey(FixedAsset, on_delete=models.CASCADE, related_name="depreciation_entries")
    period = models.ForeignKey("accounting.AccountingPeriod", on_delete=models.PROTECT, related_name="depreciation_entries")
    date = models.DateField(_("Depreciation Date"))
    amount = models.DecimalField(_("Depreciation Amount"), max_digits=15, decimal_places=2)
    journal_entry = models.OneToOneField("accounting.JournalEntry", on_delete=models.PROTECT, related_name="depreciation_source", verbose_name=_("Associated Journal Entry"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Depreciation Entry")
        verbose_name_plural = _("Depreciation Entries")
        unique_together = [("asset", "period")] # Only one depreciation per asset per period
        ordering = ["-date"]
        app_label = 'assets'

    def __str__(self):
        return f"Depreciation for {self.asset} in {self.period}: {self.amount}"

