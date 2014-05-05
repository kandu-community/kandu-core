#coding:utf-8

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import os
import re

from forms.misc import config_to_models

class Command(BaseCommand):
	# args = '<poll_id poll_id ...>'
	help = 'Updates forms to match config file'

	def handle(self, *args, **options):
		models_filename = os.path.join(settings.BASE_DIR, 'forms', 'models.py')

		try:
			with open(models_filename, 'w') as models_file:
				with open(settings.CONFIG_FILE) as config_file:
					models_file.write(config_to_models(config_file))
		except ValueError as error:
			raise CommandError(str(error))