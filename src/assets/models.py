# /home/ubuntu/accounting_project/src/assets/models.py
from django.db import models
import uuid
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
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

    def get_current_accumulated_depreciation(self):
        """Calculates the total depreciation recorded for this asset so far."""
        from django.db.models import Sum
        total = self.depreciation_entries.aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
        return total

    def calculate_depreciation_amount(self, for_date):
        """Calculates depreciation for a given period, capped at (Cost - Salvage)."""
        from decimal import Decimal
        
        # (Acquisition Cost - Salvage Value) / Useful Life in Months
        annual_depreciation = (self.acquisition_cost - self.salvage_value) / self.useful_life_years
        monthly_depreciation = annual_depreciation / 12
        suggested_amount = Decimal(monthly_depreciation).quantize(Decimal("0.01"))

        # US 9.4: Capping logic
        current_accumulated = self.get_current_accumulated_depreciation()
        max_remaining_depreciation = self.acquisition_cost - self.salvage_value - current_accumulated
        
        if max_remaining_depreciation <= 0:
            return Decimal("0.00")
            
        return min(suggested_amount, max_remaining_depreciation)

    def generate_depreciation_entry(self, period):
        """Generates a journal entry and DepreciationEntry for the given period."""
        from accounting.models import Journal, JournalEntry, EntryLine
        from decimal import Decimal
        
        amount = self.calculate_depreciation_amount(period.end_date)
        if amount <= 0:
            return None

        # Determine Journal (MISC)
        journal = Journal.objects.filter(organization=self.organization, type="MISC").first()
        if not journal:
            return None

        # Create Journal Entry
        entry = JournalEntry.objects.create(
            organization=self.organization,
            period=period,
            journal=journal,
            date=period.end_date,
            reference=f"DEP-{self.asset_code}-{period.id}",
            description=f"Depreciation for {self.name} - {period.name}"
        )

        # Dr Depreciation Expense Account
        EntryLine.objects.create(
            journal_entry=entry,
            account=self.depreciation_expense_account,
            debit_amount=amount,
            description=f"Depreciation expense: {self.name}"
        )

        # Cr Accumulated Depreciation Account
        EntryLine.objects.create(
            journal_entry=entry,
            account=self.accumulated_depreciation_account,
            credit_amount=amount,
            description=f"Acc. depreciation: {self.name}"
        )

        # Create DepreciationEntry record
        dep_entry = DepreciationEntry.objects.create(
            asset=self,
            period=period,
            date=period.end_date,
            amount=amount,
            journal_entry=entry
        )
        
        return dep_entry

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

