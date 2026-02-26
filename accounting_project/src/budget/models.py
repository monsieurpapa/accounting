# /home/ubuntu/accounting_project/src/budget/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Use string references for ForeignKey to avoid circular imports initially

class Budget(models.Model):
    """Represents an overall budget for a fiscal year."""
    STATUS_CHOICES = [
        ("DRAFT", _("Draft")),
        ("APPROVED", _("Approved")),
        ("REJECTED", _("Rejected")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="budgets")
    fiscal_year = models.ForeignKey("accounting.FiscalYear", on_delete=models.PROTECT, related_name="budgets")
    name = models.CharField(_("Budget Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default="DRAFT")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")
        unique_together = [("organization", "fiscal_year", "name")]
        app_label = 'budget'

    def __str__(self):
        return f"{self.name} ({self.fiscal_year})"

class BudgetLine(models.Model):
    """Represents a specific line item within a budget."""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="budget_lines")
    period = models.ForeignKey("accounting.AccountingPeriod", on_delete=models.PROTECT, related_name="budget_lines", null=True, blank=True, help_text=_("Optional: Specify period for monthly/quarterly budgets"))
    allocated_amount = models.DecimalField(_("Allocated Amount"), max_digits=15, decimal_places=2, default=0.00)
    # Add fields for analytical dimensions if needed

    class Meta:
        verbose_name = _("Budget Line")
        verbose_name_plural = _("Budget Lines")
        # Ensure unique budget line per account/period within a budget
        unique_together = [("budget", "account", "period")]
        app_label = 'budget'

    def __str__(self):
        period_str = f" - {self.period.name}" if self.period else ""
        return f"{self.budget.name} - {self.account}{period_str}: {self.allocated_amount}"

class BudgetCommitment(models.Model):
    """Tracks commitments made against budget lines (e.g., Purchase Orders)."""
    STATUS_CHOICES = [
        ("COMMITTED", _("Committed")),
        ("INVOICED", _("Invoiced")),
        ("CANCELLED", _("Cancelled")),
    ]
    budget_line = models.ForeignKey(BudgetLine, on_delete=models.PROTECT, related_name="commitments")
    journal_entry = models.ForeignKey("accounting.JournalEntry", on_delete=models.SET_NULL, null=True, blank=True, related_name="budget_commitments", help_text=_("Link to the actual expense entry when invoiced"))
    commitment_date = models.DateField(_("Commitment Date"))
    amount = models.DecimalField(_("Committed Amount"), max_digits=15, decimal_places=2)
    description = models.CharField(_("Description"), max_length=255)
    reference = models.CharField(_("Reference"), max_length=100, blank=True, null=True) # e.g., PO number
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default="COMMITTED")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_commitments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Budget Commitment")
        verbose_name_plural = _("Budget Commitments")
        ordering = ["-commitment_date"]
        app_label = 'budget'

    def __str__(self):
        return f"Commitment {self.id} for {self.budget_line.account}: {self.amount}"

