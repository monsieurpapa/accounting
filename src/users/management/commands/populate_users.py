import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Role, UserProfile
from organization.models import Organization


class Command(BaseCommand):
    help = 'Populate user accounts from a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Path to JSON file containing a list of users')

    def handle(self, *args, **options):
        path = options['path']
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(f'Unable to open JSON file: {e}')
            return

        if not isinstance(data, list):
            self.stderr.write('JSON payload must be a list of user objects')
            return

        for item in data:
            username = item.get('username')
            if not username:
                self.stderr.write('Skipping user entry without username')
                continue

            user, created = User.objects.get_or_create(username=username)
            # basic fields
            user.email = item.get('email', '')
            if item.get('first_name'):
                user.first_name = item['first_name']
            if item.get('last_name'):
                user.last_name = item['last_name']
            pw = item.get('password')
            if pw:
                user.set_password(pw)
            user.is_staff = item.get('is_staff', False)
            user.is_active = item.get('is_active', True)
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            org_value = item.get('organization')
            if org_value:
                try:
                    if isinstance(org_value, int):
                        org = Organization.objects.get(pk=org_value)
                    else:
                        org = Organization.objects.get(unique_code=org_value)
                    profile.organization = org
                except Organization.DoesNotExist:
                    self.stderr.write(f'Organization "{org_value}" not found for user {username}')
            role_value = item.get('role')
            if role_value:
                try:
                    profile.role = Role.objects.get(name=role_value)
                except Role.DoesNotExist:
                    self.stderr.write(f'Role "{role_value}" not found for user {username}')
            profile.save()

            self.stdout.write(f'{"Created" if created else "Updated"} user {username}')
