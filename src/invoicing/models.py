from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class Invoice(models.Model):
    """Represents a customer invoice."""
    STATUS_CHOICES = [
        ("DRAFT", _("Draft")),
        ("POSTED", _("Posted")),
        ("CANCELLED", _("Cancelled")),
    ]
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="invoices")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    customer = models.ForeignKey("cashflow.ThirdParty", on_delete=models.PROTECT, limit_choices_to={'type': 'CUSTOMER'})
    invoice_number = models.CharField(_("Invoice Number"), max_length=50, unique=True, blank=True)
    date = models.DateField(_("Invoice Date"))
    due_date = models.DateField(_("Due Date"))
    status = models.CharField(_("Status"), max_length=10, choices=STATUS_CHOICES, default="DRAFT")
    total_amount = models.DecimalField(_("Total Amount"), max_digits=15, decimal_places=2, default=0)
    journal_entry = models.OneToOneField("accounting.JournalEntry", on_delete=models.SET_NULL, null=True, blank=True, related_name="invoice_source")
    description = models.TextField(_("Description"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ["-date", "-invoice_number"]



    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.name}"

    def calculate_total(self):
        """Calculates total amount from lines."""
        self.total_amount = sum(line.total_price for line in self.lines.all())
        self.save()

    def post_to_accounting(self):
        """Creates journal entries when invoice is posted."""
        if self.status != 'POSTED' or self.journal_entry:
            return False
            
        from accounting.models import Journal, JournalEntry, EntryLine, AccountingPeriod
        
        # 1. Find/Create Journal (SALES)
        journal = Journal.objects.filter(organization=self.organization, type="SALES").first()
        if not journal:
            journal = Journal.objects.create(organization=self.organization, code="SAL", name="Sales Journal", type="SALES")
            
        # 2. Find Period
        period = AccountingPeriod.objects.filter(
            fiscal_year__organization=self.organization,
            start_date__lte=self.date,
            end_date__gte=self.date
        ).first()
        
        if not period:
            return False
            
        # 3. Create Journal Entry
        entry = JournalEntry.objects.create(
            organization=self.organization,
            period=period,
            journal=journal,
            date=self.date,
            reference=self.invoice_number,
            description=f"Invoice to {self.customer.name}"
        )
        
        # 4. Dr Accounts Receivable (Customer's receivable account)
        receivable_account = self.customer.receivable_account
        if not receivable_account:
            # Fallback or error logic depends on project requirements
            return False
            
        EntryLine.objects.create(
            journal_entry=entry,
            account=receivable_account,
            debit_amount=self.total_amount,
            description=f"Receivable from {self.customer.name}"
        )
        
        # 5. Cr Revenue (per line)
        for line in self.lines.all():
            if line.revenue_account:
                EntryLine.objects.create(
                    journal_entry=entry,
                    account=line.revenue_account,
                    credit_amount=line.total_price,
                    description=f"Revenue: {line.product.name}"
                )
                
        # 6. Post the entry
        entry.posted = True
        entry.save()
        
        self.journal_entry = entry
        self.save()
        return True

class InvoiceLine(models.Model):
    """Line item for an invoice."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("inventory.Product", on_delete=models.PROTECT)
    quantity = models.DecimalField(_("Quantity"), max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(_("Unit Price"), max_digits=15, decimal_places=2)
    total_price = models.DecimalField(_("Total Price"), max_digits=15, decimal_places=2, editable=False)
    revenue_account = models.ForeignKey("accounting.ChartOfAccounts", on_delete=models.PROTECT, related_name="invoice_lines")

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.invoice.calculate_total()

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.unit_price}"
