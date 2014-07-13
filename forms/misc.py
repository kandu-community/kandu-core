#coding:utf-8

from django.db.models import Model, ForeignKey, ImageField, DateTimeField
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models import signals
from django.contrib.gis.db.models import PointField
from model_utils.managers import InheritanceManager
from django.contrib.gis.geos import Point
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
import json
import re
import itertools
import os
import subprocess

class BaseFormModel(Model):
	user = ForeignKey(User)
	created_at = DateTimeField(auto_now_add=True)

	objects = InheritanceManager()

	show_on_map = False
	is_editable = False
	is_creatable = True
	inlines = None

	def model_name(self):
		return self.__class__.__name__

	def get_absolute_url(self):
		return reverse('web_update', kwargs={'model_name': self.model_name(), 'pk': self.pk})

	@classmethod
	def location_field(cls):
		try:
			field_name = next( field.name for field in cls._meta.fields if isinstance(field, PointField) )
		except StopIteration:
			raise AttributeError('This form has no coordinates field')
		return field_name

	@classmethod
	def verbose_name(cls):
		return cls._meta.verbose_name.title()

	def __unicode__(self):
		try:
			return u', '.join( unicode(getattr(self, field_name)) for field_name in self.label_fields if hasattr(self, field_name) and getattr(self, field_name) != None )
		except AttributeError:
			return self.__class__.verbose_name()

@receiver(signals.post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
	if created:
		group, created = Group.objects.get_or_create(name='basic')
		group.user_set.add(instance)
		group.save()

def generate_name(verbose_name):
	no_spaces = re.sub(r'\s', r'_', verbose_name.strip())
	return re.sub(r'[^_\w\d]', r'', no_spaces)

def write_group(group_verbose_names):
	for group_name in group_verbose_names:
		group, created = Group.objects.get_or_create(name=group_name)
	
	return u"\tuser_group_names = %s\n" % group_verbose_names

def write_label_fields(fields, form_object):
	field_names = []
	for field_name in fields:
		try:
			next(field for field in form_object['fields'] if field['name'] == field_name)
		except StopIteration:
			raise ValueError('Field {field_name} is referenced in "fields_for_label" of {model_name} but not defined'.format(field_name=field_name, model_name=form_object['name']))

		field_names.append(generate_name(field_name))

	return u"\tlabel_fields = %r\n" % field_names

def write_plain_fields(form_object):
	output = ''

	for field_name in ['show_on_map', 'is_editable', 'is_creatable']:
		try:
			output += u"\t{name} = {value}\n".format(value=form_object[field_name], name=field_name)
		except KeyError:
			continue

	return output

def write_visibility_dependencies(aggregate):
	if len(aggregate.keys()) == 0:
		return ''

	aggregate_processed = {
		generate_name(field_name) : {
			generate_name(other_field) : other_value
			for other_field, other_value in conditions.items()
		}
		for field_name, conditions in aggregate.items()
	}

	return u"\tvisibility_dependencies = %s\n" % aggregate_processed

def write_model(verbose_name, form_object):
	output = u"class {name}(BaseFormModel):\n\tclass Meta:\n\t\tverbose_name = u'{verbose_name}'\n\tobjects = GeoManager()\n".format(
		name=generate_name(verbose_name), 
		verbose_name=verbose_name
	)
	try:
		if form_object.get('is_creatable', True):
			output += u"\tcategory = u'{}'\n".format(form_object['category'])
		return output
	except KeyError:
		raise ValueError('%s form doesn\'t specify "category", which is mandatory' % verbose_name)

allowed_extra_args = ['help_text', 'max_length', 'to', 'choices']

def write_field(verbose_name, datatype, **extra_args):
	blank = not extra_args.pop('required', False)
	choices = [ (generate_name(verbose), verbose) for verbose in extra_args.pop('choices', []) ]
	foreignkey_to = generate_name(extra_args.pop('to', ''))


	datatype_to_field = {
		'text': ('CharField', {'max_length': 300, 'blank': blank, 'default': ''}),
		'number': ('IntegerField', {'null': blank, 'blank': blank, 'default': 0}),
		'decimal': ('DecimalField', {'null': blank, 'blank': blank, 'default': 0}),
		'boolean': ('BooleanField', {'default': False}),
		'file': ('FileField', {'upload_to': 'files', 'blank': blank, 'null':blank, 'default':''}),
		'choice': ('CharField', {'max_length': 200, 'blank': blank, 'choices': choices, 'default':''}),
		'multi-choice': ('MultiSelectField', {'max_length': 200, 'blank': blank, 'null': blank, 'choices': choices, 'default':''}),
		'foreign-key': ('ForeignKey', {'null': True, 'blank': True, 'to': foreignkey_to}),
		'many-to-many': ('ManyToManyField', {'null': True, 'blank': True, 'to': foreignkey_to}),
		'coordinates': ('PointField', {'max_length': 100, 'blank': blank, 'null': blank, 'default': Point(0,0)})
	}

	if extra_args.has_key('hint'):
		extra_args['help_text'] = extra_args.pop('hint')

	try:
		field_class, field_args = datatype_to_field[datatype]
	except KeyError:
		raise ValueError('Unknown datatype of field "%s": "%s"' % (verbose_name,datatype))

	for key in extra_args: # extra_args validation
		if key not in allowed_extra_args:
			raise ValueError('Unknown parameter for field "%s": "%s"' % (verbose_name,key))

	field_args.update(extra_args)
	# field_args['verbose_name'] = u"u'%s'" % verbose_name

	if blank: # if not requred field, no need for default value
		field_args.pop('default', None)

	field_args_str = [ '%s=%r' % (arg, value) for arg, value in field_args.items() ]

	return u'\t' + generate_name(verbose_name) + u' = ' + field_class + u'(' + u', '.join(field_args_str) + u')' + u'\n'

def create_model(form_object, collected_output, counter):
	output = ''

	output += write_model(form_object['name'], form_object)
	output += '\tdeclared_num = %d\n' % counter()
	output += write_group(form_object.get('user_groups', ['basic']))
	if form_object.has_key('fields_for_label'):
		output += write_label_fields(form_object['fields_for_label'], form_object)
	output += write_plain_fields(form_object)

	visible_when = {}
	for field_object in form_object['fields']:
		name = field_object.pop('name')
		datatype = field_object.pop('type')

		if field_object.has_key('visible_when'):
			visible_when[name] = field_object.pop('visible_when')

		output += write_field(name, datatype, **field_object)

	output += write_visibility_dependencies(visible_when)

	if form_object.has_key('inlines'):
		inlines_str = []
		for inline in form_object['inlines']:
			if isinstance(inline, basestring):
				inlines_str.append(generate_name(inline))
			elif isinstance(inline, dict):
				inline['is_creatable'] = False
				inlines_str.append(create_model(inline, collected_output, counter=counter))
			else:
				raise ValueError('"inlines" may contain only form names or json objects')

		output += '\tinlines = %r\n' % inlines_str
	
	collected_output.append(output)

	return generate_name(form_object['name'])

def config_to_models(config_file):
	'''
	Returns string with a declarations of Django models,
	generated from config_filename
	'''

	config_array = json.load(config_file)

	output = [u'''
#coding:utf-8
from django.db.models import *
from django.contrib.gis.db.models import PointField, GeoManager
from forms.misc import BaseFormModel
from multiselectfield import MultiSelectField
from django.contrib.gis.geos import Point
''']

	counter = itertools.count().next

	for form_object in config_array:
		model_and_dependent = []
		create_model(form_object, model_and_dependent, counter=counter)
		output += model_and_dependent

	return '\n'.join(output).encode('utf8')

def config_update_wrapper():
	from utils import clear_app_cache
	
	models_filename = os.path.join(settings.BASE_DIR, 'forms', 'models.py')
	try:
		with open(models_filename, 'r') as models_file:
			models_old_str = models_file.read()
	except IOError: # nothing to backup
		models_old_str = ''

	try:
		with open(settings.CONFIG_FILE) as config_file:
			with open(models_filename, 'w') as models_file:
				models_file.write(config_to_models(config_file)) # overwriting models.py with freshly generated one

			# clear_app_cache('forms.models')
			try:
				os.remove(os.path.join(settings.BASE_DIR, 'forms', 'models.pyc'))
			except OSError:
				pass

			try:
				import forms.models
				reload(forms.models)
				call_command('validate')
				# subprocess.check_output(['python', os.path.join(settings.BASE_DIR, 'manage.py'), 'validate'], stderr=subprocess.STDOUT)
			except CommandError as error:
				raise ValueError(str(error))

	except ValueError as error: # something went wrong
		with open(models_filename, 'w') as models_file:
			models_file.write(models_old_str) # rolling back models.py to initial state
		raise error

	finally:
		os.remove(os.path.join(settings.BASE_DIR, 'forms', 'models.pyc'))

