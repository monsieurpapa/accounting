from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Q, F
from .models import (
    FiscalYear, AccountingPeriod, ChartOfAccounts,
    Journal, JournalEntry, EntryLine
)

class EntryLineInline(admin.TabularInline):
    model = EntryLine
    extra = 1
    fields = ('account', 'debit_amount', 'credit_amount', 'description')
    readonly_fields = ('balance',)
    
    def balance(self, instance):
        if instance.debit_amount:
            return f"{instance.debit_amount:,.2f} D"
        return f"{instance.credit_amount:,.2f} C"
    balance.short_description = _("Balance")

@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'account_type', 'parent_account', 'is_active', 'balance_type')
    list_filter = ('account_type', 'is_active')
    search_fields = ('code', 'name', 'description')
    list_editable = ('is_active',)
    ordering = ('code',)
    
    def balance_type(self, obj):
        return 'Débit' if obj.is_debit_balance() else 'Crédit'
    balance_type.short_description = _("Balance Type")

@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'is_active', 'organization')
    list_filter = ('type', 'is_active', 'organization')
    search_fields = ('code', 'name', 'description')
    list_editable = ('is_active',)

class EntryLineInline(admin.TabularInline):
    model = EntryLine
    extra = 2
    fields = ('account', 'debit_amount', 'credit_amount', 'description')

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('entry_number', 'date', 'journal', 'reference', 'total_debit', 'total_credit', 'is_balanced', 'posted', 'created_by')
    list_filter = ('journal', 'posted', 'date', 'created_by')
    search_fields = ('entry_number', 'reference', 'description')
    date_hierarchy = 'date'
    inlines = [EntryLineInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'is_balanced')
    fieldsets = (
        (None, {
            'fields': ('organization', 'period', 'journal', 'entry_number', 'date')
        }),
        (_('Details'), {
            'fields': ('reference', 'description', 'posted')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'start_date', 'end_date', 'status', 'periods_count')
    list_filter = ('status', 'organization')
    search_fields = ('name', 'organization__name')
    date_hierarchy = 'start_date'
    
    def periods_count(self, obj):
        return obj.periods.count()
    periods_count.short_description = _('Periods')

@admin.register(AccountingPeriod)
class AccountingPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'fiscal_year', 'start_date', 'end_date', 'status', 'entries_count')
    list_filter = ('status', 'fiscal_year')
    search_fields = ('name', 'fiscal_year__name')
    date_hierarchy = 'start_date'
    
    def entries_count(self, obj):
        return obj.journal_entries.count()
    entries_count.short_description = _('Entries')

# Enable the following if you need to customize EntryLine in the admin
# @admin.register(EntryLine)
# class EntryLineAdmin(admin.ModelAdmin):
#     list_display = ('journal_entry', 'account', 'debit_amount', 'credit_amount', 'balance')
#     list_filter = ('account',)
#     search_fields = ('journal_entry__entry_number', 'description')
#     
#     def balance(self, obj):
#         if obj.debit_amount:
#             return f"{obj.debit_amount:,.2f} D"
#         return f"{obj.credit_amount:,.2f} C"
#     balance.short_description = _("Balance")