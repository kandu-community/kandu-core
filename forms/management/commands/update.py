#coding:utf-8

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
	blank = not extra_args.get('required', False)

	datatype_to_field = {
		'text': ('CharField', {'max_length': 300, 'blank': blank, 'default': ''}),
		'number': ('IntegerField', {'null': blank, 'default': 0}),
		'boolean': ('BooleanField', {'null': blank, 'default': False}),
		'file': ('FileField', {'upload_to': 'files'}),
		'choice': ('CharField', {'max_length': 5, 'choices': json.dumps( [ (str(number), verbose) for number, verbose in enumerate(extra_args['choices']) ] )}),
		'foreign-key': ('ForeignKey', {'to': generate_name(extra_args['to'])}),
	}
	#TODO: GPS-field
	#TODO: ForeignKey

	field_class, field_args = datatype_to_field[datatype]
	field_args.update(extra_args)
	field_args['verbose_name'] = verbose_name

	field_args_str = [ '{}={}'.format(arg, value) for arg, value in field_args.items() ]

	return u'\t' + generate_name(verbose_name) + u' = ' + field_class + u'(' + u', '.join(field_args_str) + u')' + u'\n'

def config_to_models(config_filename):
	'''
	Returns string with a declarations of Django models,
	generated from config_filename
	'''

	with open(config_filename) as config_file:
		config_array = json.load(config_file)

		output = u'''
		#coding:utf-8
		from django.db.models import *
		'''

		for form_object in config_array:
			output += write_model(form_object['name'])

			# write_field('user', 'foreign-key')
			for field_object in form_object['fields']:
				name = field_object.pop('name')
				datatype = field_object.pop('type')
				output += write_field(name, datatype, **field_object)

		return output

class Command(BaseCommand):
	# args = '<poll_id poll_id ...>'
	help = 'Updates forms to match config file'

	def handle(self, *args, **options):
		models_filename = os.path.join(settings.BASE_DIR, 'forms', 'models.py')

		with open(models_filename, 'w') as models_file:
			models_file.write(config_to_models(settings.CONFIG_FILE))

		call_command('schemamigration', 'forms', auto=True)
		call_command('migrate', 'forms')