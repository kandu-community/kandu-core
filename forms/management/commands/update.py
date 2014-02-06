from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import json
import os

def generate_name(verbose_name):
	#TODO: сделать реальное преобразование
	return verbose_name

def write_model(verbose_name):
	return u"class {name}(Model):\n\tclass Meta:\n\t\tverbose_name = u'{verbose_name}'\n".format(name=generate_name(verbose_name), verbose_name=verbose_name)

def write_field(verbose_name, datatype, **extra_args):
	datatype_to_field = {
		'text': u"CharField(u'{verbose_name}', max_length=500, default='')",
		'number': u"integerField(u'{verbose_name}', default=0)",
		'boolean': u"BooleanField(u'{verbose_name}', default=False)",
		'file': u"FileField(u'{verbose_name}', upload_to='files')",
		'choice': u"CharField(u'{verbose_name}', max_length=10, choices=(%s,))" % ','.join( u"('%s',u'%s')" % (generate_name(verbose_choice), verbose_choice) for verbose_choice in extra_args['choices'] )
	}
	#TODO: GPS-field
	#TODO: ForeignKey

	return (u"\t{name} = " + datatype_to_field[datatype] + u"\n").format(name=generate_name(verbose_name), verbose_name=verbose_name, **extra_args)

def config_to_models(config_filename):
	'''
	Returns string with a declarations of Django models,
	generated from config_filename
	'''

	with open(config_filename) as config_file:
		config_object = json.load(config_file)

		output = u'''
		#coding:utf-8
		from django.db.models import *
		'''

		for form_name, fields in config_object.items():
			output += write_model(form_name)

			# write_field('user', 'foreign-key')
			for field_name, field in fields.items():
				if not isinstance(field, dict):
					output += write_field(field_name, field)
				else:
					datatype = field.pop('type')
					output += write_field(field_name, datatype, **field)

		return output

class Command(BaseCommand):
	# args = '<poll_id poll_id ...>'
	help = 'Updates forms to match config file'

	def handle(self, *args, **options):
		models_filename = os.path.join(settings.BASE_DIR, 'forms', 'models.py')

		with open(models_filename, 'w') as models_file:
			models_file.write(config_to_models)

		call_command('schemamigration', 'forms --auto')
		call_command('migrate', 'forms')