# /home/ubuntu/accounting_project/src/cashflow/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Use string references for ForeignKey to avoid circular imports initially

class ThirdParty(models.Model):
    """Represents Suppliers, Customers, Donors, etc."""
    TYPE_CHOICES = [
        ("SUPPLIER", _("Supplier")),
        ("CUSTOMER", _("Customer")),
        ("DONOR", _("Donor")),
        ("EMPLOYEE", _("Employee")),
        ("OTHER", _("Other")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="third_parties")
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES)
    contact_info = models.TextField(_("Contact Information"), blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    tax_id = models.CharField(_("Tax ID"), max_length=50, blank=True, null=True)
    # Link to specific receivable/payable accounts in ChartOfAccounts if needed
    # receivable_account = models.ForeignKey("accounting.ChartOfAccounts", ...)
    # payable_account = models.ForeignKey("accounting.ChartOfAccounts", ...)
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _("Third Party")
        verbose_name_plural = _("Third Parties")
        unique_together = [("organization", "name", "type")]
        app_label = 'cashflow'

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class PaymentReceiptBase(models.Model):
    """Abstract base class for Payments and Receipts."""
    PAYMENT_METHOD_CHOICES = [
        ("CASH", _("Cash")),
        ("CHEQUE", _("Cheque")),
        ("TRANSFER", _("Bank Transfer")),
        ("MOBILE", _("Mobile Money")),
        ("OTHER", _("Other")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.PROTECT)
    third_party = models.ForeignKey(ThirdParty, on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField(_("Date"), db_index=True)
    amount = models.DecimalField(_("Amount"), max_digits=15, decimal_places=2)
    payment_method = models.CharField(_("Payment Method"), max_length=10, choices=PAYMENT_METHOD_CHOICES)
    reference = models.CharField(_("Reference"), max_length=255, blank=True, null=True) # Cheque no, transaction ID
    description = models.TextField(_("Description"), blank=True, null=True)
    journal_entry = models.OneToOneField("accounting.JournalEntry", on_delete=models.PROTECT, verbose_name=_("Associated Journal Entry"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-date"]
        app_label = 'cashflow'

class Payment(PaymentReceiptBase):
    """Represents a payment made."""
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        app_label = 'cashflow'

    def __str__(self):
        return f"Payment {self.id} ({self.date}) - {self.amount}"

class Receipt(PaymentReceiptBase):
    """Represents a receipt received."""
    class Meta:
        verbose_name = _("Receipt")
        verbose_name_plural = _("Receipts")
        app_label = 'cashflow'

    def __str__(self):
        return f"Receipt {self.id} ({self.date}) - {self.amount}"

class BankReconciliation(models.Model):
    """Manages the bank reconciliation process."""
    STATUS_CHOICES = [
        ("DRAFT", _("Draft")),
        ("RECONCILED", _("Reconciled")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="reconciliations")
    # Limit choices in the form/admin, not strictly in the model unless using a specific manager
    bank_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="reconciliations")
    statement_date = models.DateField(_("Statement Date"))
    statement_end_balance = models.DecimalField(_("Statement Ending Balance"), max_digits=15, decimal_places=2)
    calculated_ledger_balance = models.DecimalField(_("Calculated Ledger Balance"), max_digits=15, decimal_places=2)
    difference = models.DecimalField(_("Difference"), max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(_("Status"), max_length=15, choices=STATUS_CHOICES, default="DRAFT")
    reconciled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reconciliations_done")
    reconciled_at = models.DateTimeField(_("Reconciled At"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Bank Reconciliation")
        verbose_name_plural = _("Bank Reconciliations")
        unique_together = [("bank_account", "statement_date")]
        ordering = ["-statement_date"]
        app_label = 'cashflow'

    def __str__(self):
        return f"Reconciliation for {self.bank_account} as of {self.statement_date}"

