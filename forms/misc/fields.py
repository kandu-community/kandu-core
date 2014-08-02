import re

from mixins import *
from functions import generate_name


def get_field_class(datatype):
	class_name = ''.join(part.capitalize() for part in datatype.split('-'))
	try:
		FieldClass = globals()[class_name]
	except KeyError as error:
		raise ValueError('Unknown type %r of field %r' % ())
	return FieldClass

def load_field(json_object, parent=None):
	try:
		datatype = json_object['type']
	except KeyError as error:
		raise ValueError('Field is missing %r param. This info might help you locate the field: %r' % (error.args[0], json_object))

	FieldClass = get_field_class(datatype)
	return FieldClass(parent=parent, **json_object)

class Field(TreeMixin, DjangoRenderMixin, JSONRenderMixin, ParamsMixin, Base):
	type = str()
	name = str()
	hint = str()
	required = False
	label_field = False

	_django_class = None
	_conditions = None

	def __init__(self, *args, **kwargs):
		try:
			self.name = kwargs['name']
		except KeyError as error:
			raise ValueError('Field is missing \'name\' parameter. This info might help you locate the field: %r' % kwargs)

		self._conditions_container = ConditionsContainer(parent=self)

		self.type = self.get_type()
		self._conditions = [Condition(field=field, value=value) for field, value in kwargs.pop('visible_when', {}).items()]

		super(Field, self).__init__(*args, **kwargs)

	def children(self):
		return [self._conditions_container] # TODO: should return visible_when

	@classmethod
	def get_type(cls):
		class_name = cls.__name__
		return re.sub('([a-z0-9])([A-Z])', r'\1-\2', re.sub('(.)([A-Z][a-z]+)', r'\1-\2', class_name)).lower()

	def insert_children_json(self, json_object):
		if self._conditions:
			json_object['visible_when'] = {condition.field: condition.value for condition in self._conditions}

class ConditionsContainer(TreeMixin, Base):
	name = 'visible_when'

	def children(self):
		return self._parent._conditions

	def insertChild(self):
		self._parent._conditions.append(Condition(field='choose field', parent=self))

	def removeChildren(self, position, number):
		self._parent._conditions[position:position+number] = []

class Condition(TreeMixin, ParamsMixin, Base):
	field = str()
	value = str()

	_combobox_field = 'field'

	def get_combobox_choices(self):
		return [field.name for field in self._parent._fields]

	@property
	def name(self):
		return '%s == %s' % (self.field, self.value)

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

	def render_schema(self):
		schema = super(Form, self).render_schema()
		schema['choices'] = 'List'
		return schema

class ToMixin(ComboboxEditorMixin):
	to = str()

	_combobox_field = 'to'

	def get_django_args(self):
		django_args = super(ToMixin, self).get_django_args()
		django_args['to'] = generate_name(django_args.pop('to'))
		return django_args

	def get_combobox_choices(self):
		item = self._parent
		while item._parent: # go up the tree to the root
			item = item._parent
		return [form.name for form in item.children()] + ['']

	def get_json_params(self):
		if self.to == '':
			raise ValueError('Foreign-key field %r at form %r is missing "to" parameter value' % (self.name, self._parent.name))
		else:
			return super(ToMixin, self).get_json_params()

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
	_django_class = 'PointField'
	default = None

	def get_django_args(self):
		django_args = super(NullValueMixin, self).get_django_args()

		if not django_args['default']:
			from django.contrib.gis.geos import Point
			django_args['default'] = Point(0,0)
		return django_args