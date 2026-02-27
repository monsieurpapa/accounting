from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
import tempfile
import json

class OrganizationAdminTests(TestCase):
    def setUp(self):
        # use superuser for admin management RBAC
        self.staff = User.objects.create_superuser(username='orgadmin', password='pass', email='orgadmin@example.com')
        self.client = Client()
        self.client.force_login(self.staff)

    def test_org_list_accessible(self):
        url = reverse('organization:organization_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_org_create_update_and_delete(self):
        url = reverse('organization:organization_add')
        response = self.client.post(url, {
            'name': 'Test Org',
            'unique_code': 'TO',
            'is_active': True,
        })
        self.assertEqual(response.status_code, 302)
        from organization.models import Organization
        self.assertTrue(Organization.objects.filter(name='Test Org').exists())
        org = Organization.objects.get(name='Test Org')

        # update
        update_url = reverse('organization:organization_edit', args=[org.pk])
        response = self.client.post(update_url, {
            'name': 'Test Org Updated',
            'unique_code': 'TO',
            'is_active': False,
        })
        self.assertEqual(response.status_code, 302)
        org.refresh_from_db()
        self.assertEqual(org.name, 'Test Org Updated')
        self.assertFalse(org.is_active)

        delurl = reverse('organization:organization_delete', args=[org.pk])
        response = self.client.post(delurl)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Organization.objects.filter(name='Test Org Updated').exists())

    def test_populate_organizations_command(self):
        data = [{'name': 'Alpha', 'unique_code': 'A1'}]
        tmp = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
        json.dump(data, tmp)
        tmp.flush()
        tmp.close()
        call_command('populate_organizations', tmp.name)
        from organization.models import Organization
        self.assertTrue(Organization.objects.filter(name='Alpha').exists())
