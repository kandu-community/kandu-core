from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
	help = 'Performs an initial setup of everything'

	def handle(self, *args, **options):
		call_command('syncdb')

		call_command('schemamigration', 'forms --initial')
		call_command('migrate', 'forms')