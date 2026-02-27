from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounting.models import ChartOfAccounts, FiscalYear, AccountingPeriod

class ReportingViewTests(TestCase):
    def setUp(self):
        # create a user and ensure it has a profile with an organization
        self.user = User.objects.create_user(username='reporter', password='pass', is_staff=True)
        self.client = Client()
        self.client.force_login(self.user)
        # the profile creation signal will attach a default org
        self.org = self.user.profile.organization
        # create some basic fixtures that multiple reports will use
        self.account = ChartOfAccounts.objects.create(
            organization=self.org,
            code='4000',
            name='Revenue Account',
            account_type='REVENUE'
        )
        self.fy = FiscalYear.objects.create(
            organization=self.org,
            name='FY2025',
            start_date='2025-01-01',
            end_date='2025-12-31'
        )
        self.period = AccountingPeriod.objects.create(
            fiscal_year=self.fy,
            name='Q1 2025',
            start_date='2025-01-01',
            end_date='2025-03-31'
        )

    def test_export_url_preserves_query_params(self):
        url = reverse('reporting:general_ledger')
        query = '?account=%s&fiscal_year=%s' % (self.account.pk, self.fy.pk)
        response = self.client.get(url + query)
        self.assertEqual(response.status_code, 200)
        pdf_url = response.context['export_pdf_url']
        # should include both original parameters and the format override
        self.assertIn('account=%s' % self.account.pk, pdf_url)
        self.assertIn('fiscal_year=%s' % self.fy.pk, pdf_url)
        self.assertTrue(pdf_url.endswith('format=pdf'))

    def _assert_export_response(self, view_name, params, expected_content_type):
        """Helper to issue a GET request with format parameter and check content type."""
        url = reverse('reporting:' + view_name)
        query = params + '&format=' + ('pdf' if expected_content_type == 'application/pdf' else 'xlsx')
        response = self.client.get(url + '?' + query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], expected_content_type)

    def test_general_ledger_export_pdf(self):
        self._assert_export_response('general_ledger', 'account=%s' % self.account.pk, 'application/pdf')
        self._assert_export_response('general_ledger', 'account=%s' % self.account.pk, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_balance_sheet_export(self):
        # balance sheet doesn't require additional parameters
        self._assert_export_response('balance_sheet', '', 'application/pdf')
        self._assert_export_response('balance_sheet', '', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_income_statement_export(self):
        # need either fiscal_year or period to generate result
        self._assert_export_response('income_statement', 'fiscal_year=%s' % self.fy.pk, 'application/pdf')
        self._assert_export_response('income_statement', 'fiscal_year=%s' % self.fy.pk, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_trial_balance_export(self):
        # like income statement, also needs timeframe
        self._assert_export_response('trial_balance', 'fiscal_year=%s' % self.fy.pk, 'application/pdf')
        self._assert_export_response('trial_balance', 'fiscal_year=%s' % self.fy.pk, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
