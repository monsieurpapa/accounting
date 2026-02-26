# /home/ubuntu/accounting_project/src/budget/models.py
from django.db import models
import uuid
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
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

    def approve(self):
        """Approves the budget, making it active for controls."""
        self.status = "APPROVED"
        self.save()

class BudgetLine(models.Model):
    """Represents a specific line item within a budget."""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="lines")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
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

    def get_committed_amount(self):
        """Calculates total amount currently committed but not yet invoiced."""
        from django.db.models import Sum
        total = self.commitments.filter(status='COMMITTED').aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
        return total

    def get_actual_spent(self):
        """Calculates the actual amount spent against this budget line."""
        from accounting.models import EntryLine
        from decimal import Decimal
        qs = EntryLine.objects.filter(
            account=self.account,
            journal_entry__posted=True
        )
        if self.period:
            qs = qs.filter(journal_entry__period=self.period)
        else:
            qs = qs.filter(journal_entry__period__fiscal_year=self.budget.fiscal_year)
            
        summary = qs.aggregate(
            debit=models.Sum('debit_amount'),
            credit=models.Sum('credit_amount')
        )
        
        debit = summary['debit'] or Decimal("0.00")
        credit = summary['credit'] or Decimal("0.00")
        
        # For Expense accounts: Balance = Debit - Credit
        # For Revenue accounts: Balance = Credit - Debit
        if self.account.account_type == 'EXPENSE':
            return debit - credit
        elif self.account.account_type == 'REVENUE':
            return credit - debit
        return debit - credit # Default

    @property
    def variance(self):
        """Traditional variance: Budget - Actual."""
        return self.allocated_amount - self.get_actual_spent()

    @property
    def funds_available(self):
        """Executive view: Budget - Actual - Committed."""
        return self.allocated_amount - self.get_actual_spent() - self.get_committed_amount()

    @property
    def variance_percentage(self):
        if self.allocated_amount == 0:
            return 0
        return (self.variance / self.allocated_amount) * 100

class BudgetCommitment(models.Model):
    """Tracks commitments made against budget lines (e.g., Purchase Orders)."""
    STATUS_CHOICES = [
        ("COMMITTED", _("Committed")),
        ("INVOICED", _("Invoiced")),
        ("CANCELLED", _("Cancelled")),
    ]
    budget_line = models.ForeignKey(BudgetLine, on_delete=models.PROTECT, related_name="commitments")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
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

