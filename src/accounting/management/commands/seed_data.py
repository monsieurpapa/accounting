"""
Management command to populate realistic test/demo data across all implemented
features of the accounting system (SYSCOHADA-compliant, DRC context).

Usage:
    python manage.py seed_data [--reset]

Options:
    --reset    Delete all existing data before seeding (use with caution!)
"""

import random
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from organization.models import Organization
from accounting.models import (
    ChartOfAccounts, Journal, FiscalYear, AccountingPeriod,
    JournalEntry, EntryLine, Project
)
from budget.models import Budget, BudgetLine
from cashflow.models import ThirdParty, Payment, Receipt, BankReconciliation
from assets.models import DepreciationMethod, FixedAsset


class Command(BaseCommand):
    help = "Seed the database with realistic demo data for all features."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            self._reset_data()

        self.stdout.write(self.style.MIGRATE_HEADING("=== Seeding Demo Data ==="))

        org = self._seed_organization()
        admin_user = self._seed_users(org)
        accounts = self._seed_chart_of_accounts(org)
        journals = self._seed_journals(org)
        fiscal_year, periods = self._seed_fiscal_year(org)
        projects = self._seed_projects(org)
        self._seed_journal_entries(org, journals, accounts, periods, projects, admin_user)
        self._seed_budgets(org, fiscal_year, accounts, periods)
        self._seed_third_parties(org, accounts)
        self._seed_assets(org, accounts, periods)

        self.stdout.write(self.style.SUCCESS("\n✅  Demo data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("   Login: admin@demo.com / admin123"))

    # -----------------------------------------------------------------------
    def _reset_data(self):
        BankReconciliation.objects.all().delete()
        Receipt.objects.all().delete()
        Payment.objects.all().delete()
        ThirdParty.objects.all().delete()
        FixedAsset.objects.all().delete()
        DepreciationMethod.objects.all().delete()
        BudgetLine.objects.all().delete()
        Budget.objects.all().delete()
        EntryLine.objects.all().delete()
        JournalEntry.objects.all().delete()
        AccountingPeriod.objects.all().delete()
        FiscalYear.objects.all().delete()
        Project.objects.all().delete()
        Journal.objects.all().delete()
        ChartOfAccounts.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    # -----------------------------------------------------------------------
    def _seed_organization(self):
        org, _ = Organization.objects.get_or_create(
            name="Cabinet UBS Congo SARL",
            defaults={
                "address": "Boulevard du 30 Juin, Kinshasa, DRC",
                "contact_info": "+243 81 234 5678 | contact@ubscongo.com",
                "unique_code": "UBS-KIN-001",
                "is_active": True,
            }
        )
        self.stdout.write(f"  ✔ Organisation: {org.name}")
        return org

    # -----------------------------------------------------------------------
    def _seed_users(self, org):
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@demo.com",
                password="admin123",
                first_name="Admin",
                last_name="Système"
            )
        else:
            admin = User.objects.get(username="admin")

        # Regular accountant
        if not User.objects.filter(username="comptable").exists():
            User.objects.create_user(
                username="comptable",
                email="comptable@ubscongo.com",
                password="compta123",
                first_name="Marie",
                last_name="Mukendi"
            )

        self.stdout.write("  ✔ Utilisateurs créés (admin / comptable)")
        return admin

    # -----------------------------------------------------------------------
    def _seed_chart_of_accounts(self, org):
        """SYSCOHADA-compliant chart of accounts."""
        accounts_data = [
            # ASSETS
            ("1", "Capitaux", "EQUITY"),
            ("10", "Capital", "EQUITY"),
            ("101", "Capital social", "EQUITY"),
            ("11", "Réserves", "EQUITY"),
            ("111", "Réserve légale", "EQUITY"),
            ("12", "Report à nouveau", "EQUITY"),
            ("13", "Résultat de l'exercice", "EQUITY"),
            # LIABILITIES
            ("16", "Emprunts et dettes assimilées", "LIABILITY"),
            ("401", "Fournisseurs", "LIABILITY"),
            ("402", "Fournisseurs - Effets à payer", "LIABILITY"),
            ("44", "État et collectivités publiques", "LIABILITY"),
            ("441", "État - TVA collectée", "LIABILITY"),
            ("442", "État - TVA déductible", "ASSET"),
            ("421", "Personnel - Rémunérations dues", "LIABILITY"),
            ("422", "Personnel - Acomptes et avances", "ASSET"),
            # ASSETS
            ("2", "Immobilisations", "ASSET"),
            ("21", "Immobilisations incorporelles", "ASSET"),
            ("22", "Terrains", "ASSET"),
            ("23", "Bâtiments", "ASSET"),
            ("24", "Matériel", "ASSET"),
            ("241", "Matériel informatique", "ASSET"),
            ("242", "Mobilier de bureau", "ASSET"),
            ("28", "Amortissements des immobilisations", "ASSET"),
            ("281", "Amortissement - Matériel informatique", "ASSET"),
            ("282", "Amortissement - Mobilier de bureau", "ASSET"),
            ("3", "Stocks", "ASSET"),
            ("31", "Marchandises", "ASSET"),
            ("32", "Matières premières", "ASSET"),
            ("4", "Tiers", "ASSET"),
            ("41", "Clients", "ASSET"),
            ("411", "Clients - Ventes de biens et services", "ASSET"),
            ("412", "Clients - Effets à recevoir", "ASSET"),
            # BANK & CASH
            ("5", "Trésorerie", "ASSET"),
            ("51", "Banques", "ASSET"),
            ("511", "Banque Equity BCDC", "ASSET"),
            ("512", "Banque RawBank", "ASSET"),
            ("57", "Caisse", "ASSET"),
            ("571", "Caisse principale", "ASSET"),
            # EXPENSES
            ("6", "Charges", "EXPENSE"),
            ("60", "Achats", "EXPENSE"),
            ("601", "Achats de marchandises", "EXPENSE"),
            ("602", "Achats de matières premières", "EXPENSE"),
            ("61", "Transports", "EXPENSE"),
            ("611", "Transport sur achats", "EXPENSE"),
            ("62", "Services extérieurs", "EXPENSE"),
            ("621", "Loyers et charges locatives", "EXPENSE"),
            ("622", "Frais de téléphone et internet", "EXPENSE"),
            ("623", "Frais de publicité", "EXPENSE"),
            ("63", "Impôts et taxes", "EXPENSE"),
            ("631", "Impôts directs", "EXPENSE"),
            ("64", "Charges de personnel", "EXPENSE"),
            ("641", "Rémunérations du personnel", "EXPENSE"),
            ("645", "Charges sociales", "EXPENSE"),
            ("66", "Charges financières", "EXPENSE"),
            ("661", "Intérêts des emprunts", "EXPENSE"),
            ("68", "Dotations aux amortissements", "EXPENSE"),
            ("681", "DAP sur immobilisations", "EXPENSE"),
            # REVENUE
            ("7", "Produits", "REVENUE"),
            ("70", "Ventes", "REVENUE"),
            ("701", "Ventes de marchandises", "REVENUE"),
            ("702", "Prestations de services", "REVENUE"),
            ("703", "Prestations de conseil", "REVENUE"),
            ("71", "Production stockée", "REVENUE"),
            ("75", "Autres produits", "REVENUE"),
            ("751", "Produits divers de gestion courante", "REVENUE"),
            ("77", "Produits financiers", "REVENUE"),
            ("771", "Intérêts des prêts", "REVENUE"),
        ]
        account_map = {}
        for code, name, acct_type in accounts_data:
            acc, _ = ChartOfAccounts.objects.get_or_create(
                organization=org, code=code,
                defaults={"name": name, "account_type": acct_type, "is_active": True}
            )
            account_map[code] = acc

        self.stdout.write(f"  ✔ Plan comptable: {len(accounts_data)} comptes (SYSCOHADA)")
        return account_map

    # -----------------------------------------------------------------------
    def _seed_journals(self, org):
        journals_data = [
            ("VTE", "Journal des Ventes", "SALES"),
            ("ACH", "Journal des Achats", "PURCHASE"),
            ("BNK", "Journal de Banque", "BANK"),
            ("CAI", "Journal de Caisse", "CASH"),
            ("OD", "Opérations Diverses", "MISC"),
            ("OUV", "Ouverture", "OPENING"),
        ]
        d = {}
        for code, name, jtype in journals_data:
            j, _ = Journal.objects.get_or_create(
                organization=org, code=code,
                defaults={"name": name, "type": jtype, "is_active": True}
            )
            d[code] = j
        self.stdout.write(f"  ✔ Journaux: {len(journals_data)} journaux créés")
        return d

    # -----------------------------------------------------------------------
    def _seed_fiscal_year(self, org):
        fy, _ = FiscalYear.objects.get_or_create(
            organization=org,
            name="Exercice 2025",
            defaults={
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 12, 31),
                "status": "OPEN",
            }
        )
        month_names = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        periods = []
        for i in range(1, 13):
            start = date(2025, i, 1)
            if i < 12:
                end = date(2025, i + 1, 1) - timedelta(days=1)
            else:
                end = date(2025, 12, 31)
            p, _ = AccountingPeriod.objects.get_or_create(
                fiscal_year=fy, name=f"{month_names[i-1]} 2025",
                defaults={"start_date": start, "end_date": end, "status": "OPEN"}
            )
            periods.append(p)

        self.stdout.write(f"  ✔ Exercice fiscal 2025 avec 12 périodes")
        return fy, periods

    # -----------------------------------------------------------------------
    def _seed_projects(self, org):
        projects_data = [
            ("PRJ-001", "Audit Externe - MINAFEC", "Mission d'audit externe pour le Ministère des Finances"),
            ("PRJ-002", "Conseil Fiscal - Gécamines", "Conseil en optimisation fiscale pour Gécamines"),
            ("PRJ-003", "Formation Comptable", "Formation des agents comptables de l'administration publique"),
            ("PRJ-004", "Digitalisation RDC", "Projet de numérisation des archives comptables"),
            ("SVC-001", "Service Paie Mensuelle", "Service de gestion mensuelle de la paie"),
            ("SVC-002", "Tenue de Comptabilité", "Comptabilité externalisée PME"),
        ]
        project_list = []
        for code, name, desc in projects_data:
            p, _ = Project.objects.get_or_create(
                organization=org, code=code,
                defaults={"name": name, "description": desc, "is_active": True}
            )
            project_list.append(p)
        self.stdout.write(f"  ✔ Projets & Services: {len(projects_data)} créés")
        return project_list

    # -----------------------------------------------------------------------
    def _seed_journal_entries(self, org, journals, accounts, periods, projects, user):
        """Create realistic journal entries across different periods."""
        entries_created = 0

        # Helper shortcuts
        def make_entry(journal_code, period_idx, dt, ref, desc, lines, project=None):
            nonlocal entries_created
            period = periods[period_idx]
            entry = JournalEntry(
                organization=org,
                period=period,
                journal=journals[journal_code],
                date=dt,
                reference=ref,
                description=desc,
                created_by=user,
            )
            entry.save()
            for acc_code, debit, credit, line_desc in lines:
                EntryLine.objects.create(
                    journal_entry=entry,
                    account=accounts[acc_code],
                    debit_amount=debit,
                    credit_amount=credit,
                    description=line_desc,
                    project=project,
                )
            entries_created += 1
            return entry

        # ---- January: Opening Balance ----
        make_entry("OUV", 0, date(2025, 1, 1), "OUV-2025-001", "Bilan d'ouverture 2025", [
            ("511", Decimal("25000000"), None, "Solde Banque Equity BCDC"),
            ("571", Decimal("5000000"), None, "Solde Caisse principale"),
            ("41",  Decimal("8500000"), None, "Clients à recouvrer"),
            ("241", Decimal("12000000"), None, "Matériel informatique (VNC)"),
            ("242", Decimal("3500000"), None, "Mobilier de bureau (VNC)"),
            ("101", None, Decimal("45000000"), "Capital social"),
            ("11",  None, Decimal("9000000"), "Réserves diverses"),
        ])

        # ---- January: Sales invoices ----
        make_entry("VTE", 0, date(2025, 1, 15), "FAC-2025-001", "Facturation Audit MINAFEC - Phase 1",
            [
                ("411", Decimal("7500000"), None, "Facture client MINAFEC"),
                ("702", None, Decimal("7500000"), "Produits de mission d'audit"),
            ], project=projects[0])

        make_entry("VTE", 0, date(2025, 1, 22), "FAC-2025-002", "Facturation Conseil Fiscal Gécamines",
            [
                ("411", Decimal("4200000"), None, "Facture client Gécamines"),
                ("703", None, Decimal("4200000"), "Produits de conseil fiscal"),
            ], project=projects[1])

        # ---- January: Expenses ----
        make_entry("ACH", 0, date(2025, 1, 10), "ACH-2025-001", "Achat fournitures de bureau",
            [
                ("601", Decimal("450000"), None, "Fournitures de bureau"),
                ("401", None, Decimal("450000"), "Fournisseur Elais SARL"),
            ])

        make_entry("BNK", 0, date(2025, 1, 25), "VRT-2025-001", "Loyer bureau janvier 2025",
            [
                ("621", Decimal("2500000"), None, "Loyer mensuel bureaux Gombe"),
                ("511", None, Decimal("2500000"), "Banque Equity BCDC"),
            ])

        make_entry("CAI", 0, date(2025, 1, 31), "CAI-2025-001", "Dépenses de caisse - transport janvier",
            [
                ("611", Decimal("320000"), None, "Transport et déplacements"),
                ("571", None, Decimal("320000"), "Caisse principale"),
            ])

        # ---- February: Payroll ----
        make_entry("OD", 1, date(2025, 2, 28), "SAL-2025-02", "Paie du personnel - Février 2025",
            [
                ("641", Decimal("6800000"), None, "Salaires nets à payer"),
                ("645", Decimal("1360000"), None, "Charges sociales patronales"),
                ("421", None, Decimal("6800000"), "Personnel - Rémunérations dues"),
                ("44",  None, Decimal("1360000"), "CNSS et cotisations"),
            ], project=projects[4])

        make_entry("BNK", 1, date(2025, 2, 28), "VRT-2025-004", "Règlement salaires Février 2025",
            [
                ("421", Decimal("6800000"), None, "Apurement salaires"),
                ("511", None, Decimal("6800000"), "Virement bancaire salaires"),
            ])

        # ---- March: New client receipts ----
        make_entry("BNK", 2, date(2025, 3, 5), "REC-2025-001", "Encaissement MINAFEC - Facture FAC-2025-001",
            [
                ("511", Decimal("7500000"), None, "Virement reçu MINAFEC"),
                ("411", None, Decimal("7500000"), "Apurement créance MINAFEC"),
            ], project=projects[0])

        make_entry("VTE", 2, date(2025, 3, 10), "FAC-2025-005", "Facturation Formation Comptable Q1",
            [
                ("411", Decimal("3600000"), None, "Facture Formation Q1"),
                ("702", None, Decimal("3600000"), "Produits de formation"),
            ], project=projects[2])

        # ---- April: Purchases and equipment ----
        make_entry("ACH", 3, date(2025, 4, 2), "ACH-2025-010", "Achat matériel informatique",
            [
                ("241", Decimal("5200000"), None, "Laptop HP EliteBook x3"),
                ("401", None, Decimal("5200000"), "Fournisseur TechShop SARL"),
            ])

        make_entry("BNK", 3, date(2025, 4, 15), "VRT-2025-010", "Règlement fournisseur TechShop",
            [
                ("401", Decimal("5200000"), None, "Apurement dette fournisseur"),
                ("511", None, Decimal("5200000"), "Paiement Equity BCDC"),
            ])

        # ---- May ----
        make_entry("VTE", 4, date(2025, 5, 1), "FAC-2025-020", "Facturation Tenue Comptabilité Mai",
            [
                ("411", Decimal("1800000"), None, "Facture service comptabilité"),
                ("701", None, Decimal("1800000"), "Services comptables externalisés"),
            ], project=projects[5])

        make_entry("BNK", 4, date(2025, 5, 20), "VRT-2025-020", "Loyers bureau mai 2025",
            [
                ("621", Decimal("2500000"), None, "Loyer mensuel - mai"),
                ("511", None, Decimal("2500000"), "Banque Equity BCDC"),
            ])

        # ---- June ----
        make_entry("OD", 5, date(2025, 6, 30), "DAP-2025-06", "Dotations aux amortissements - H1 2025",
            [
                ("681", Decimal("950000"), None, "DAP matériel informatique"),
                ("281", None, Decimal("950000"), "Amortissement cumulé matériel info"),
            ])

        make_entry("OD", 5, date(2025, 6, 30), "DAP-2025-06B", "DAP Mobilier de bureau H1 2025",
            [
                ("681", Decimal("350000"), None, "DAP mobilier bureau"),
                ("282", None, Decimal("350000"), "Amortissement cumulé mobilier"),
            ])

        # ---- July ----
        make_entry("VTE", 6, date(2025, 7, 15), "FAC-2025-030", "Digitalisation RDC - Tranche 2",
            [
                ("411", Decimal("9000000"), None, "Facture projet digitalisation"),
                ("703", None, Decimal("9000000"), "Honoraires conseil digitalisation"),
            ], project=projects[3])

        # ---- August ----
        make_entry("ACH", 7, date(2025, 8, 5), "ACH-2025-030", "Achat licences logiciels",
            [
                ("602", Decimal("1200000"), None, "Licences Microsoft 365"),
                ("401", None, Decimal("1200000"), "Fournisseur MicroSoft Partner"),
            ])

        make_entry("BNK", 7, date(2025, 8, 12), "VRT-2025-030", "Règlement licences logiciels",
            [
                ("401", Decimal("1200000"), None, "Apurement fournisseur MS"),
                ("511", None, Decimal("1200000"), "Paiement Equity BCDC"),
            ])

        # ---- September: Payroll ----
        make_entry("OD", 8, date(2025, 9, 30), "SAL-2025-09", "Paie du personnel - Septembre 2025",
            [
                ("641", Decimal("7200000"), None, "Salaires septembre"),
                ("645", Decimal("1440000"), None, "Charges sociales septembre"),
                ("421", None, Decimal("7200000"), "Personnel - Rémunérations dues"),
                ("44",  None, Decimal("1440000"), "CNSS/INSS septembre"),
            ], project=projects[4])

        self.stdout.write(f"  ✔ Écritures comptables: {entries_created} écritures créées")

    # -----------------------------------------------------------------------
    def _seed_budgets(self, org, fiscal_year, accounts, periods):
        budget, _ = Budget.objects.get_or_create(
            organization=org,
            fiscal_year=fiscal_year,
            name="Budget Opérationnel 2025",
            defaults={
                "description": "Budget annuel couvrant toutes les charges et produits prévus pour 2025",
                "status": "APPROVED",
            }
        )

        lines_data = [
            ("702", Decimal("50000000")),  # Prestations de services
            ("703", Decimal("30000000")),  # Conseil
            ("701", Decimal("15000000")),  # Ventes marchandises
            ("641", Decimal("85000000")),  # Salaires
            ("645", Decimal("17000000")),  # Charges sociales
            ("621", Decimal("30000000")),  # Loyers
            ("622", Decimal("3600000")),   # Téléphone
            ("601", Decimal("5000000")),   # Achats
            ("681", Decimal("6000000")),   # Amortissements
            ("611", Decimal("2400000")),   # Transport
            ("631", Decimal("4000000")),   # Impôts
        ]
        for acc_code, amount in lines_data:
            BudgetLine.objects.get_or_create(
                budget=budget,
                account=accounts[acc_code],
                period=None,
                defaults={"allocated_amount": amount}
            )

        self.stdout.write(f"  ✔ Budget 2025 (Approuvé) avec {len(lines_data)} lignes")

    # -----------------------------------------------------------------------
    def _seed_third_parties(self, org, accounts):
        parties_data = [
            ("Ministère des Finances (MINAFEC)", "CUSTOMER", "minafec@finances.gouv.cd", "+243 81 000 0001"),
            ("Gécamines SA", "CUSTOMER", "compta@gecamines.cd", "+243 81 000 0002"),
            ("Administration Publique DRC", "CUSTOMER", "ap@rdc.cd", "+243 82 000 0001"),
            ("Elais SARL", "SUPPLIER", "elais@sarl.cd", "+243 89 111 0001"),
            ("TechShop SARL", "SUPPLIER", "tech@techshop.cd", "+243 89 222 0002"),
            ("MicroSoft Partner RDC", "SUPPLIER", "partner@ms.cd", "+243 89 000 9999"),
            ("CNSS/INSS RDC", "OTHER", "info@cnss.cd", "+243 81 555 0001"),
        ]
        for name, ptype, contact, phone in parties_data:
            ThirdParty.objects.get_or_create(
                organization=org,
                name=name,
                type=ptype,
                defaults={
                    "contact_info": f"{contact} | {phone}",
                    "address": "Kinshasa, DRC",
                    "receivable_account": accounts.get("411") if ptype == "CUSTOMER" else None,
                    "payable_account": accounts.get("401") if ptype == "SUPPLIER" else None,
                    "bank_account": accounts.get("511"),
                    "is_active": True,
                }
            )
        self.stdout.write(f"  ✔ Tiers: {len(parties_data)} tiers créés")

    # -----------------------------------------------------------------------
    def _seed_assets(self, org, accounts, periods):
        dep_method, _ = DepreciationMethod.objects.get_or_create(
            name="Linéaire (Straight-Line)",
            defaults={"calculation_logic": "Coût - Valeur résiduelle / Durée de vie en années"}
        )

        assets_data = [
            ("MAT-001", "Serveur Dell PowerEdge", "Serveur principal",
             date(2024, 6, 15), Decimal("8500000"), 5, Decimal("500000"), "241"),
            ("MAT-002", "Laptop HP EliteBook (x5)", "Ordinateurs portables pour consultants",
             date(2025, 1, 10), Decimal("12000000"), 3, Decimal("0"), "241"),
            ("MOB-001", "Bureaux et chaises de direction (x10)", "Mobilier salle de réunion",
             date(2023, 9, 1), Decimal("4500000"), 10, Decimal("200000"), "242"),
            ("MOB-002", "Climatiseurs (x4)", "Climatisation bureaux",
             date(2024, 3, 20), Decimal("3200000"), 7, Decimal("100000"), "242"),
        ]

        for code, name, desc, acq_date, cost, life, salvage, acc_code in assets_data:
            FixedAsset.objects.get_or_create(
                organization=org,
                asset_code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "acquisition_date": acq_date,
                    "acquisition_cost": cost,
                    "asset_account": accounts[acc_code],
                    "accumulated_depreciation_account": accounts["281" if acc_code == "241" else "282"],
                    "depreciation_expense_account": accounts["681"],
                    "depreciation_method": dep_method,
                    "useful_life_years": life,
                    "salvage_value": salvage,
                    "status": "ACTIVE",
                }
            )

        self.stdout.write(f"  ✔ Immobilisations: {len(assets_data)} actifs créés")
