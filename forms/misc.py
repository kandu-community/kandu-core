#coding:utf-8

from django.db.models import Model, ForeignKey
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models import signals
from model_utils.managers import InheritanceManager
import json
import re

class BaseFormModel(Model):
	user = ForeignKey(User)

	objects = InheritanceManager()

	def model_name(self):
		return self.__class__.__name__

	@classmethod
	def verbose_name(cls):
		return cls._meta.verbose_name.title()

@receiver(signals.post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
	if created:
		group, created = Group.objects.get_or_create(name='basic')
		group.user_set.add(instance)
		group.save()

		#TODO: это не сохраняется

def generate_name(verbose_name):
	no_spaces = re.sub(r'\s', r'_', verbose_name)
	return re.sub(r'[^_\w\d]', r'', no_spaces)

def write_group(group_verbose_name):
	group, created = Group.objects.get_or_create(name=group_verbose_name)
	return u"\tuser_group_name = u'%s'\n" % group_verbose_name

def write_model(verbose_name):
	return u"class {name}(BaseFormModel):\n\tclass Meta:\n\t\tverbose_name = u'{verbose_name}'\n".format(name=generate_name(verbose_name), verbose_name=verbose_name)

def write_field(verbose_name, datatype, **extra_args):
	blank = not extra_args.pop('required', False)
	choices = [ (generate_name(verbose), verbose) for verbose in extra_args.pop('choices', []) ]

	name_extra = ''
	if datatype == 'foreign-key' and extra_args.pop('hidden', None):
		name_extra = '_hidden'

	datatype_to_field = {
		'text': ('CharField', {'max_length': 300, 'blank': blank, 'default': "''"}),
		'number': ('IntegerField', {'null': blank, 'default': 0}),
		'boolean': ('BooleanField', {'default': False}),
		'file': ('FileField', {'upload_to': "'files'", 'null': blank}),
		'choice': ('CharField', {'max_length': 200, 'blank': blank, 'choices': choices}),
		'multi-choice': ('MultiSelectField', {'max_length': 200, 'blank': blank, 'choices': choices}),
		'foreign-key': ('ForeignKey', {'null': blank, 'to': "'%s'" % generate_name(extra_args.pop('to', ''))}),
		'coordinates': ('CoordinatesField', {'max_length': 100, 'blank': blank})
	}

	try:
		field_class, field_args = datatype_to_field[datatype]
	except KeyError:
		raise ValueError("Unknown datatype in config: " + datatype)
	field_args.update(extra_args)
	field_args['verbose_name'] = u"u'%s'" % verbose_name

	field_args_str = [ '{}={}'.format(arg, value) for arg, value in field_args.items() ]

	return u'\t' + generate_name(verbose_name) + name_extra + u' = ' + field_class + u'(' + u', '.join(field_args_str) + u')' + u'\n'

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
from multiselectfield import MultiSelectField
'''

	for form_object in config_array:
		output += write_model(form_object['name'])
		output += write_group(form_object.get('user_group', 'basic'))

		for field_object in form_object['fields']:
			name = field_object.pop('name')
			datatype = field_object.pop('type')

			output += write_field(name, datatype, **field_object)

	return output