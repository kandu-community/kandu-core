from django.contrib.gis.geos import Point
import re

from functions import generate_name
from mixins import *


def load_field(json_object):
	try:
		class_name = ''.join(part.capitalize() for part in json_object['type'].split('-'))
	except KeyError as error:
		raise ValueError('Field is missing %r param. This info might help you locate the field: %r' % (error.args[0], json_object))
	
	try:
		FieldClass = globals()[class_name]
	except KeyError as error:
		raise ValueError('Unknown type %r of field %r' % ())
	return FieldClass(**json_object)

class Field(DjangoRenderMixin, ParamsMixin, QtMixin, object):
	type = str()
	name = str()
	# visible_when = dict()
	hint = str()
	
	required = False

	_django_class = None

	def __init__(self, **kwargs):
		try:
			self.name = kwargs['name']
		except KeyError as error:
			raise ValueError('Field is missing \'name\' parameter. This info might help you locate the field: %r' % kwargs)

	def children(self):
		return [] # TODO: should return visible_when

	def _type(self):
		class_name = self.__class__.__name__
		return re.sub('([a-z0-9])([A-Z])', r'\1-\2', re.sub('(.)([A-Z][a-z]+)', r'\1-\2', class_name)).lower()

class DefaultStringMixin(object):
	default = ''

class NullValueMixin(object):
	def get_django_args(self):
		django_args = super(NullValueMixin, self).get_django_args()
		django_args['null'] = django_args['blank']
		return django_args

class ChoicesMixin(object):
	choices = list()

	def get_django_args(self):
		django_args = super(ChoicesMixin, self).get_django_args()
		django_args['choices'] = [ (generate_name(verbose), verbose) for verbose in django_args.pop('choices', []) ]
		return django_args

class ToMixin(object):
	to = str()

	def get_django_args(self):
		django_args = super(ToMixin, self).get_django_args()
		django_args['to'] = generate_name(django_args.pop('to'))
		return django_args

class Text(DefaultStringMixin, Field):
	max_length = 300
	_django_class = 'CharField'

class Number(NullValueMixin, Field):
	default = 0
	_django_class = 'IntegerField'

class Decimal(NullValueMixin, Field):
	default = 0
	_django_class = 'DecimalField'

class Boolean(Field):
	default = False
	_django_class = 'BooleanField'

	def get_django_args(self):
		django_args = {name: value for name, value in dir(self).items() if not name.startswith('_') or callable(value)} # NOTE: is_callable?
		return django_args

class File(DefaultStringMixin, NullValueMixin, Field):
	_django_class = 'FileField'

	def get_django_args(self):
		django_args = super(File, self).get_django_args()
		django_args['upload_to'] = 'files'
		return django_args

class Choice(DefaultStringMixin, ChoicesMixin, Field):
	max_length = 200
	_django_class = 'CharField'

class MultiChoice(DefaultStringMixin, ChoicesMixin, Field):
	max_length = 200
	_django_class = 'MultiSelectField'

class ForeignKey(NullValueMixin, ToMixin, Field):
	_django_class = 'ForeignKey'

class ManyToMany(NullValueMixin, ToMixin, Field):
	_django_class = 'ManyToManyField'

class Coordinates(NullValueMixin, Field):
	max_length = 100
	default = Point(0,0)
	_django_class = 'PointField'