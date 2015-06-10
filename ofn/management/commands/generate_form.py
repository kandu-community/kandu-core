# coding:utf-8

import json

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Generate stock movement form for Kandu app'

    def handle(self, *args, **options):
        forms = []
        for user in User.objects.all():
            if hasattr(user, 'profile') and user.profile.token:
                forms.append(self.generate_form(user))

        config = []

        with file(settings.CONFIG_FILE, 'rb') as config_file:
            source = config_file.read()
            config = json.loads(source)

        # First remove any existing stock movement forms so we don't duplicate forms
        new_config = [form for form in config if not form['name'].startswith('Stock')]

        # Slide the stock movement forms onto the end
        new_config.extend(forms)

        with file(settings.CONFIG_FILE, 'wb') as config_file:
            source = json.dumps(new_config, indent=4)
            config_file.write(source)

    def generate_form(self, user):
        variant_choices = {}

        for p in user.product_set.all():
            for v in p.variant_set.all():
                variant_choices[v.id] = '%s - %s' % (p, v)

        form_schema = {
            'category': 'Produce',
            'name': 'Stock',
            'is_creatable': True,
            'fields': [
                {
                    "label_field": True,
                    "name": "Product",
                    "required": True,
                    "choices": variant_choices,
                    "max_length": 200,
                    "type": "choice",
                },
                {
                    "label_field": True,
                    "default": 0,
                    "required": True,
                    "name": "Quantity",
                    "type": "number",
                }
            ],
            'user_groups': [
                'basic',
            ],
            'is_editable': True,
            'inlines': [],
            'cache_submissions_offline': False,
            'show_on_map': True,
        }

        return form_schema
