import re

from mixins import *
from functions import generate_name, get_available_fields


def get_field_class(datatype):
	class_name = ''.join(part.capitalize() for part in datatype.split('-'))
	try:
		FieldClass = globals()[class_name]
	except KeyError as error:
		raise ValueError('Unknown type %r of field' % error)
	return FieldClass

def load_field(json_object, parent=None):
	try:
		datatype = json_object['type']
	except KeyError as error:
		raise ValueError('Field is missing %r param. This info might help you locate the field: %r' % (error.args[0], json_object))

	FieldClass = get_field_class(datatype)
	return FieldClass(parent=parent, **json_object)

class Field(TreeMixin, DjangoRenderMixin, JSONRenderMixin, Base):
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
		except KeyError:
			raise ValueError('Field is missing \'name\' parameter. This info might help you locate the field: %r' % kwargs)

		self.type = self.get_type()
		self._conditions = [Condition(field=field, value=value, parent=self) for field, value in kwargs.pop('visible_when', {}).items()]

		super(Field, self).__init__(*args, **kwargs)

	def get_django_args(self):
		self.validate()
		return super(Field, self).get_django_args()

	def validate(self):
		pass

	@classmethod
	def get_type(cls):
		class_name = cls.__name__
		return re.sub('([a-z0-9])([A-Z])', r'\1-\2', re.sub('(.)([A-Z][a-z]+)', r'\1-\2', class_name)).lower()

	def insert_children_json(self, json_object):
		if self._conditions:
			json_object['visible_when'] = {condition.field: condition.value for condition in self._conditions}

	def render_schema(self):
		schema = super(Field, self).render_schema()
		schema['type'] = {
			'type': 'Select',
			'options': [field_class.get_type() for field_name, field_class in get_available_fields()]
		}
		schema['required'] = 'Checkbox'
		schema['label_field'] = 'Checkbox'
		return schema

	def node_kind(self):
		return 'field'

	def children(self):
		return self._conditions

	def insertChild(self):
		self._conditions.append(Condition(parent=self))
		return self._conditions[-1]

	def removeChildren(self, node):
		self._conditions.remove(node)

class Condition(TreeMixin, Base):
	field = str()
	value = str()

	_combobox_field = 'field'

	def get_combobox_choices(self):
		return [field.name for field in self._parent._fields]

	@property
	def name(self):
		return '%s == %s' % (self.field, self.value)

	def load_data(self, data):
		updated_params = []
		for attr_name in ['field', 'value']:
			if getattr(self, attr_name) != data.get(attr_name, getattr(self, attr_name)):
				updated_params.append(attr_name)

		self.populate_params(**data)

		return updated_params

	def render_schema(self):
		schema = super(Condition, self).render_schema()
		schema.pop('name') # it is a calculated and therefore read only field
		schema['field'] = {'type': 'Select', 'options': [field.name for field in self.parent_form()._fields]}
		return schema

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
		schema = super(ChoicesMixin, self).render_schema()
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
		return [form.name for form in item.children()]

	def get_json_params(self):
		if self.to == '':
			raise ValueError('Foreign-key field %r at form %r is missing "to" parameter value' % (self.name, self._parent.name))
		else:
			return super(ToMixin, self).get_json_params()

	def render_schema(self):
		schema = super(ToMixin, self).render_schema()
		schema['to'] = {'type': 'Select', 'options': self.get_combobox_choices()}
		return schema

class NumericFieldMixin(object):
	def get_django_args(self):
		django_args = super(NumericFieldMixin, self).get_django_args()
		django_args['max_digits'] = int(django_args['max_length'])
		django_args['decimal_places'] = int(django_args.pop('max_length')) / 2
		return django_args

class Text(DefaultStringMixin, Field):
	max_length = 300
	_django_class = 'CharField'

class Date(NullValueMixin, Field):
	_django_class = 'DateField'

	def get_django_args(self):
		django_args = super(Date, self).get_django_args()

		if not django_args.get('default', None):
			from datetime import date
			django_args['default'] = date(1999,1,1)
		return django_args

class Number(NullValueMixin, Field):
	default = 0
	_django_class = 'IntegerField'

class Decimal(NullValueMixin, NumericFieldMixin, Field):
	default = 0
	max_length = 5
	_django_class = 'DecimalField'

class Boolean(Field):
	default = False
	_django_class = 'BooleanField'

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
		django_args = super(Coordinates, self).get_django_args()

		if not django_args.get('default', None):
			from django.contrib.gis.geos import Point
			django_args['default'] = Point(0,0)
		return django_args

class IdField(DefaultStringMixin, Field):
	max_length = 100
	_django_class = 'DjangoIdField'
	from_fields = list()

	def validate(self):
		actual_fields = [field.name for field in self.parent_form()._fields]
		for field_name in self.from_fields:
			if field_name not in actual_fields:
				raise ValueError('"from_fields" of "%s" field mentions "%s", but there is no such field' 
					% (self.name, field_name))

	def render_schema(self):
		schema = super(IdField, self).render_schema()
		# schema['from_fields'] = {
		# 	'type': 'List',
		# 	'itemType': {
		# 		'type': 'Select', 
		# 		'options': [field.name for field in self.parent_form()._fields]
		# 	}
		# }
		schema['from_fields'] = 'List'
		return schema

	def get_django_args(self):
		django_args = super(IdField, self).get_django_args()
		django_args['from_fields'] = [generate_name(verbose_name) for verbose_name in self.from_fields]
		django_args['editable'] = False
		return django_args