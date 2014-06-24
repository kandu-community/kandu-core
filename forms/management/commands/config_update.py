#coding:utf-8

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import os
import re

from forms.misc import config_update_wrapper

class Command(BaseCommand):
	help = 'Updates forms to match config file'

	def handle(self, *args, **options):
		try:
			config_update_wrapper()
		except ValueError as error:
			raise CommandError(str(error))