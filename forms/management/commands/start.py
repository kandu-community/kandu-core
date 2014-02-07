from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
	help = 'Performs an initial setup of everything'

	def handle(self, *args, **options):
		call_command('syncdb')

		call_command('schemamigration', 'forms', initial=True)
		call_command('migrate', 'forms', fake=True)