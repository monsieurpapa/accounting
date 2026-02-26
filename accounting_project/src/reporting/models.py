# /home/ubuntu/accounting_project/src/reporting/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Use string references for ForeignKey to avoid circular imports initially

class ReportTemplate(models.Model):
    """Defines templates for standard and custom reports."""
    REPORT_TYPE_CHOICES = [
        ("BALANCE_SHEET", _("Balance Sheet")),
        ("INCOME_STATEMENT", _("Income Statement")),
        ("CASH_FLOW", _("Cash Flow Statement")),
        ("BUDGET_VS_ACTUAL", _("Budget vs Actual")),
        ("CUSTOM", _("Custom Report")),
        # Add other standard reports as needed
    ]
    name = models.CharField(_("Report Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    type = models.CharField(_("Report Type"), max_length=20, choices=REPORT_TYPE_CHOICES)
    configuration_json = models.JSONField(_("Configuration (JSON)"), blank=True, null=True, help_text=_("Stores structure/parameters for custom reports"))
    is_standard = models.BooleanField(_("Is Standard Report"), default=False)

    class Meta:
        verbose_name = _("Report Template")
        verbose_name_plural = _("Report Templates")
        app_label = 'reporting'

    def __str__(self):
        return self.name

class GeneratedReport(models.Model):
    """Stores instances of generated reports."""
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, related_name="generated_reports")
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT, related_name="generated_reports")
    generation_date = models.DateTimeField(_("Generation Datetime"), auto_now_add=True)
    start_date = models.DateField(_("Report Start Date"), null=True, blank=True)
    end_date = models.DateField(_("Report End Date"))
    parameters_json = models.JSONField(_("Parameters Used (JSON)"), blank=True, null=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_reports")
    file = models.FileField(_("Report File"), upload_to="reports/%Y/%m/", null=True, blank=True) # Store PDF/XLS

    class Meta:
        verbose_name = _("Generated Report")
        verbose_name_plural = _("Generated Reports")
        ordering = ["-generation_date"]
        app_label = 'reporting'

    def __str__(self):
        return f"{self.template.name} generated on {self.generation_date}"

