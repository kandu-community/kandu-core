#coding:utf-8

from django.db.models import Model, ForeignKey
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager
import json

class BaseFormModel(Model):
	user = ForeignKey(User)

	objects = InheritanceManager()

	def model_name(self):
		return self.__class__.__name__

	@classmethod
	def verbose_name(cls):
		return cls._meta.verbose_name.title()

def generate_name(verbose_name):
	#TODO: сделать реальное преобразование
	return verbose_name.lower().replace(' ', '_')

def write_model(verbose_name):
	return u"class {name}(BaseFormModel):\n\tclass Meta:\n\t\tverbose_name = u'{verbose_name}'\n".format(name=generate_name(verbose_name), verbose_name=verbose_name)

def write_field(verbose_name, datatype, **extra_args):
	blank = not extra_args.pop('required', False)

	datatype_to_field = {
		'text': ('CharField', {'max_length': 300, 'blank': blank, 'default': "''"}),
		'number': ('IntegerField', {'null': blank, 'default': 0}),
		'boolean': ('BooleanField', {'default': False}),
		'file': ('FileField', {'upload_to': "'files'", 'null': blank}),
		'choice': ('CharField', {'max_length': 200, 'blank': blank, 'choices': [ (generate_name(verbose), verbose) for verbose in extra_args.pop('choices', []) ]}),
		'foreign-key': ('ForeignKey', {'to': "'%s'" % generate_name(extra_args.pop('to', ''))}),
		'coordinates': ('CoordinatesField', {'max_length': 100, 'blank': blank})
	}
	#TODO: multi-choice

	try:
		field_class, field_args = datatype_to_field[datatype]
	except KeyError:
		raise ValueError("Unknown datatype in config: " + datatype)
	field_args.update(extra_args)
	field_args['verbose_name'] = u"u'%s'" % verbose_name

	field_args_str = [ '{}={}'.format(arg, value) for arg, value in field_args.items() ]

	return u'\t' + generate_name(verbose_name) + u' = ' + field_class + u'(' + u', '.join(field_args_str) + u')' + u'\n'

def config_to_models(config_file):
	'''
	Returns string with a declarations of Django models,
	generated from config_filename
	'''

	config_array = json.load(config_file)

	output = u'''
#coding:utf-8
from django.db.models import *
from forms.fields import CoordinatesField
from forms.misc import BaseFormModel
'''

	for form_object in config_array:
		output += write_model(form_object['name'])

		# write_field('user', 'foreign-key')
		for field_object in form_object['fields']:
			name = field_object.pop('name')
			datatype = field_object.pop('type')
			output += write_field(name, datatype, **field_object)

	return output