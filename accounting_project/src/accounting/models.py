# /home/ubuntu/accounting_project/src/accounting/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Use string references for ForeignKey to avoid circular imports initially

class FiscalYear(models.Model):
    """Defines accounting fiscal years."""
    STATUS_CHOICES = [
        ("OPEN", _("Open")),
        ("CLOSED", _("Closed")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="fiscal_years")
    name = models.CharField(_("Fiscal Year Name"), max_length=100) # e.g., "2024-2025"
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default="OPEN")

    class Meta:
        verbose_name = _("Fiscal Year")
        verbose_name_plural = _("Fiscal Years")
        unique_together = [("organization", "name"), ("organization", "start_date"), ("organization", "end_date")]
        ordering = ["-start_date"]
        app_label = 'accounting'

    def __str__(self):
        # Accessing organization name might require loading the related object
        # Consider optimizing if used frequently in lists
        return f"{self.organization_id} - {self.name}" # Use organization_id for efficiency

class AccountingPeriod(models.Model):
    """Defines accounting periods within a fiscal year (e.g., months)."""
    STATUS_CHOICES = [
        ("OPEN", _("Open")),
        ("CLOSED", _("Closed")),
    ]
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name="periods")
    name = models.CharField(_("Period Name"), max_length=100) # e.g., "January 2024"
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default="OPEN")

    class Meta:
        verbose_name = _("Accounting Period")
        verbose_name_plural = _("Accounting Periods")
        unique_together = [("fiscal_year", "name"), ("fiscal_year", "start_date")]
        ordering = ["start_date"]
        app_label = 'accounting'

    def __str__(self):
        return f"{self.fiscal_year} - {self.name}"

class ChartOfAccounts(models.Model):
    """Represents an account in the Chart of Accounts (SYSCOHADA compliant)."""
    ACCOUNT_TYPE_CHOICES = [
        ("ASSET", _("Asset")),
        ("LIABILITY", _("Liability")),
        ("EQUITY", _("Equity")),
        ("REVENUE", _("Revenue")),
        ("EXPENSE", _("Expense")),
        ("OTHER", _("Other")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="accounts")
    code = models.CharField(_("Account Code"), max_length=50) # SYSCOHADA code
    name = models.CharField(_("Account Name"), max_length=255)
    account_type = models.CharField(_("Account Type"), max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    parent_account = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child_accounts", verbose_name=_("Parent Account"))
    description = models.TextField(_("Description"), blank=True, null=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    # Add fields for analytical accounting if needed

    class Meta:
        verbose_name = _("Chart of Accounts")
        verbose_name_plural = _("Charts of Accounts")
        unique_together = [("organization", "code")]
        ordering = ["code"]
        app_label = 'accounting'

    def __str__(self):
        return f"{self.code} - {self.name}"

class Journal(models.Model):
    """Represents accounting journals (e.g., Sales, Purchase, Bank)."""
    JOURNAL_TYPE_CHOICES = [
        ("SALES", _("Sales")),
        ("PURCHASE", _("Purchase")),
        ("BANK", _("Bank")),
        ("CASH", _("Cash")),
        ("MISC", _("Miscellaneous")),
        ("OPENING", _("Opening Balance")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="journals")
    code = models.CharField(_("Journal Code"), max_length=10)
    name = models.CharField(_("Journal Name"), max_length=100)
    type = models.CharField(_("Journal Type"), max_length=10, choices=JOURNAL_TYPE_CHOICES)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Journal")
        verbose_name_plural = _("Journals")
        unique_together = [("organization", "code")]
        app_label = 'accounting'

    def __str__(self):
        return f"{self.code} - {self.name}"

class JournalEntry(models.Model):
    """Represents a single accounting transaction header."""
    SYNC_STATUS_CHOICES = [
        ("SYNCED", _("Synced")),
        ("PENDING", _("Pending Sync")),
        ("ERROR", _("Sync Error")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.PROTECT, related_name="journal_entries")
    period = models.ForeignKey(AccountingPeriod, on_delete=models.PROTECT, related_name="journal_entries")
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT, related_name="journal_entries")
    entry_number = models.CharField(_("Entry Number"), max_length=50, unique=True) # Consider auto-generation strategy
    date = models.DateField(_("Date"), db_index=True)
    reference = models.CharField(_("Reference"), max_length=255, blank=True, null=True) # e.g., Invoice number
    description = models.TextField(_("Description"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_entries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted = models.BooleanField(_("Posted"), default=False, db_index=True, help_text=_("Indicates if the entry is finalized and posted to the ledger."))
    sync_status = models.CharField(_("Sync Status"), max_length=10, choices=SYNC_STATUS_CHOICES, default="SYNCED", help_text=_("Status for offline synchronization"))
    # Add field for reversal if needed: reversed_entry = models.OneToOneField("self", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")
        ordering = ["-date", "-created_at"]
        app_label = 'accounting'

    def __str__(self):
        return f"Entry {self.entry_number} ({self.date})"

    # Properties for balance check (consider moving logic to managers or services for complex calculations)
    @property
    def total_debit(self):
        # Ensure Decimal usage if not implicitly handled
        from decimal import Decimal
        return sum(line.debit_amount for line in self.lines.all() if line.debit_amount) or Decimal("0.00")

    @property
    def total_credit(self):
        from decimal import Decimal
        return sum(line.credit_amount for line in self.lines.all() if line.credit_amount) or Decimal("0.00")

    @property
    def is_balanced(self):
        # Use Decimal comparison for accuracy
        return self.total_debit == self.total_credit

class EntryLine(models.Model):
    """Represents a line item within a Journal Entry."""
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name="entry_lines")
    debit_amount = models.DecimalField(_("Debit"), max_digits=15, decimal_places=2, null=True, blank=True)
    credit_amount = models.DecimalField(_("Credit"), max_digits=15, decimal_places=2, null=True, blank=True)
    description = models.CharField(_("Line Description"), max_length=255, blank=True, null=True)
    # Add fields for analytical dimensions if needed

    class Meta:
        verbose_name = _("Entry Line")
        verbose_name_plural = _("Entry Lines")
        ordering = ["id"] # Keep insertion order by default
        app_label = 'accounting'
        # Add constraint to ensure either debit or credit is filled, but not both (if required)
        # models.CheckConstraint(check=Q(debit_amount__isnull=False) | Q(credit_amount__isnull=False), name='debit_or_credit_filled')
        # models.CheckConstraint(check=~(Q(debit_amount__isnull=False) & Q(credit_amount__isnull=False)), name='debit_or_credit_not_both')

    def __str__(self):
        amount = self.debit_amount if self.debit_amount else self.credit_amount
        type = "Dr" if self.debit_amount else "Cr"
        return f"{self.account} - {amount} ({type})"

