import json
from django.core.management.base import BaseCommand
from organization.models import Organization


class Command(BaseCommand):
    help = 'Populate organizations from a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Path to JSON file containing a list of organizations')

    def handle(self, *args, **options):
        path = options['path']
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(f'Unable to open JSON file: {e}')
            return

        if not isinstance(data, list):
            self.stderr.write('JSON payload must be a list of organization objects')
            return

        for item in data:
            name = item.get('name')
            if not name:
                self.stderr.write('Skipping organization entry without a name')
                continue
            defaults = {
                'address': item.get('address', ''),
                'contact_info': item.get('contact_info', ''),
                'unique_code': item.get('unique_code', ''),
                'is_active': item.get('is_active', True),
            }
            org, created = Organization.objects.update_or_create(name=name, defaults=defaults)
            self.stdout.write(f'{"Created" if created else "Updated"} organization {name}')
