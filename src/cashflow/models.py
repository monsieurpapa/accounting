# /home/ubuntu/accounting_project/src/cashflow/models.py
from django.db import models
import uuid
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES)
    contact_info = models.TextField(_("Contact Information"), blank=True, null=True)
    address = models.TextField(_("Address"), blank=True, null=True)
    tax_id = models.CharField(_("Tax ID"), max_length=50, blank=True, null=True)
    # Link to specific receivable/payable accounts in ChartOfAccounts
    receivable_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="receivable_third_parties", null=True, blank=True)
    payable_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="payable_third_parties", null=True, blank=True)
    bank_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="bank_third_parties", null=True, blank=True, help_text=_("Default bank account for this third party if applicable"))
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    third_party = models.ForeignKey(ThirdParty, on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField(_("Date"), db_index=True)
    amount = models.DecimalField(_("Amount"), max_digits=15, decimal_places=2)
    payment_method = models.CharField(_("Payment Method"), max_length=10, choices=PAYMENT_METHOD_CHOICES)
    reference = models.CharField(_("Reference"), max_length=255, blank=True, null=True) # Cheque no, transaction ID
    description = models.TextField(_("Description"), blank=True, null=True)
    journal_entry = models.OneToOneField("accounting.JournalEntry", on_delete=models.PROTECT, verbose_name=_("Associated Journal Entry"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-date"]
        app_label = 'cashflow'

    def create_journal_entry(self):
        """Automatically creates a journal entry for the payment/receipt."""
        from accounting.models import Journal, JournalEntry, EntryLine, AccountingPeriod, FiscalYear
        
        # Determine Journal (Cash or Bank)
        journal_type = "CASH" if self.payment_method == "CASH" else "BANK"
        journal = Journal.objects.filter(organization=self.organization, type=journal_type).first()
        if not journal:
            # Fallback or raise error? For now, fallback to MISC
            journal = Journal.objects.filter(organization=self.organization, type="MISC").first()
        
        if not journal:
            return None # Cannot create entry without journal

        # Find Accounting Period
        period = AccountingPeriod.objects.filter(
            fiscal_year__organization=self.organization,
            start_date__lte=self.date,
            end_date__gte=self.date
        ).first()
        
        if not period:
            return None # Cannot create entry without period

        # Create Journal Entry Header
        entry = JournalEntry.objects.create(
            organization=self.organization,
            period=period,
            journal=journal,
            date=self.date,
            reference=self.reference or f"Auto-{self._meta.model_name.upper()}-{self.id}",
            description=self.description or f"{self._meta.verbose_name}: {self.third_party}"
        )
        return entry

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and not self.journal_entry:
            entry = self.create_journal_entry()
            if entry:
                self.journal_entry = entry
                self.create_entry_lines(entry)
                # Update with the new journal_entry link without triggering recursive save if possible
                # or just use update
                self.__class__.objects.filter(pk=self.pk).update(journal_entry=entry)

    def create_entry_lines(self, entry):
        """To be implemented by subclasses."""
        pass

class Payment(PaymentReceiptBase):
    """Represents a payment made."""
    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        app_label = 'cashflow'

    def __str__(self):
        return f"Payment {self.id} ({self.date}) - {self.amount}"

    def create_entry_lines(self, entry):
        from accounting.models import EntryLine
        # Payment: Dr Liability/Expense, Cr Bank/Cash
        # For simplicity, assume ThirdParty has a payable account
        target_account = None
        if self.third_party:
            target_account = self.third_party.payable_account
        
        # Fallback: if no target account, this is a gap that needs configuration
        if target_account:
            # Dr Target Account
            EntryLine.objects.create(
                journal_entry=entry,
                account=target_account,
                debit_amount=self.amount,
                description=self.description
            )
            
            # Cr Bank/Cash Account
            # Need to know WHICH bank/cash account. For now, assume a configured one on ThirdParty or fallback
            cash_account = None
            if self.third_party and self.third_party.bank_account:
                cash_account = self.third_party.bank_account
            
            if cash_account:
                EntryLine.objects.create(
                    journal_entry=entry,
                    account=cash_account,
                    credit_amount=self.amount,
                    description=self.description
                )

class Receipt(PaymentReceiptBase):
    """Represents a receipt received."""
    class Meta:
        verbose_name = _("Receipt")
        verbose_name_plural = _("Receipts")
        app_label = 'cashflow'

    def __str__(self):
        return f"Receipt {self.id} ({self.date}) - {self.amount}"

    def create_entry_lines(self, entry):
        from accounting.models import EntryLine
        # Receipt: Dr Bank/Cash, Cr Revenue/Asset/Receivable
        target_account = None
        if self.third_party:
            target_account = self.third_party.receivable_account
            
        if target_account:
            # Cr Target Account
            EntryLine.objects.create(
                journal_entry=entry,
                account=target_account,
                credit_amount=self.amount,
                description=self.description
            )
            
            # Dr Bank/Cash Account
            cash_account = None
            if self.third_party and self.third_party.bank_account:
                cash_account = self.third_party.bank_account
            
            if cash_account:
                EntryLine.objects.create(
                    journal_entry=entry,
                    account=cash_account,
                    debit_amount=self.amount,
                    description=self.description
                )

class BankReconciliation(models.Model):
    """Manages the bank reconciliation process."""
    STATUS_CHOICES = [
        ("DRAFT", _("Draft")),
        ("RECONCILED", _("Reconciled")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="reconciliations")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
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

    def calculate_balances(self):
        """Calculates the ledger balance and adjusted bank balance."""
        from accounting.models import EntryLine
        from decimal import Decimal
        
        # 1. Full Ledger Balance (all posted entries for this account up to date)
        ledger_summary = EntryLine.objects.filter(
            account=self.bank_account,
            journal_entry__posted=True,
            journal_entry__date__lte=self.statement_date
        ).aggregate(
            debit=models.Sum('debit_amount'),
            credit=models.Sum('credit_amount')
        )
        ledger_debit = ledger_summary['debit'] or Decimal("0.00")
        ledger_credit = ledger_summary['credit'] or Decimal("0.00")
        self.calculated_ledger_balance = ledger_debit - ledger_credit

        # 2. Adjusted Balance (Outstanding items)
        # Outstanding items = Ledger items that are NOT cleared
        outstanding_summary = EntryLine.objects.filter(
            account=self.bank_account,
            journal_entry__posted=True,
            journal_entry__date__lte=self.statement_date,
            is_cleared=False
        ).aggregate(
            debit=models.Sum('debit_amount'),
            credit=models.Sum('credit_amount')
        )
        outstanding_debits = outstanding_summary['debit'] or Decimal("0.00") # Deposits in transit
        outstanding_credits = outstanding_summary['credit'] or Decimal("0.00") # Outstanding checks

        # Statement Balance = Ledger Balance - Deposits in Transit + Outstanding Checks
        # Wait, if I have $100 in ledger, but $20 is a deposit in transit, statement has $80.
        # If I have $100 in ledger, but $30 check is outstanding, statement has $130 (since I deducted it in ledger but bank didn't).
        
        # So: Reconciled Balance = Statement Balance + Deposits in Transit - Outstanding Checks
        # This Reconciled Balance should equal the Ledger Balance.
        
        # Alternatively: Expected Statement Balance = Ledger Balance - Outstanding Deposits + Outstanding Checks
        expected_statement_balance = self.calculated_ledger_balance - outstanding_debits + outstanding_credits
        
        self.difference = self.statement_end_balance - expected_statement_balance
        return self.calculated_ledger_balance

    def reconcile(self, user):
        """Finalizes the reconciliation and marks matched items as cleared."""
        from django.utils import timezone
        from accounting.models import EntryLine
        if self.difference == 0:
            # Mark all items up to this date as cleared if they weren't before
            # Note: In a real system, the user would select specific items.
            # Here we assume everything not marked as outstanding matches the statement.
            # For simplicity, we mark everything up to statement_date as cleared.
            EntryLine.objects.filter(
                account=self.bank_account,
                journal_entry__posted=True,
                journal_entry__date__lte=self.statement_date,
                is_cleared=False
            ).update(is_cleared=True, cleared_at=self.statement_date)

            self.status = "RECONCILED"
            self.reconciled_by = user
            self.reconciled_at = timezone.now()
            self.save()
            return True
        return False

