import time
import random
from itertools import izip, repeat
from collections import OrderedDict
from hashlib import md5

from functions import generate_name


class Base(object): # workaround for "object.__init__() takes no parameters"
	def __init__(self, *args, **kwargs):
		self._id = kwargs.pop('id', None) or md5(str(time.time()) + str(random.randint(1,420)) + self.name).hexdigest()
		self.populate_params(**kwargs)

	def populate_params(self, **kwargs):
		for name, value in kwargs.items():
			if hasattr(self, name):
				setattr(self, name, value)
			else:
				from fields import Field
				raise ValueError('Unknown parameter %r for %s %r' % (name, 'field' if isinstance(self, Field) else 'form', kwargs['name']))

class DjangoRenderMixin(object):
	def get_django_args(self):
		django_args = {name: getattr(self, name) for name in dir(self) if not name.startswith('_') and not callable(getattr(self, name))}
		django_args['blank'] = not django_args.pop('required')
		django_args['help_text'] = django_args.pop('hint')

		for name in ['visible_when', 'type', 'name', 'label_field']:
			django_args.pop(name, None)
		return django_args

	def render_django(self):
		django_args = self.get_django_args()
		if not self.required:
			django_args.pop('default', None)

		field_args_str = [ '%s=%r' % (arg, value) for arg, value in django_args.items() ]
		return u'\t' + generate_name(self.name) + u' = ' + self._django_class + u'(' + u', '.join(field_args_str) + u')' + u'\n'

class JSONRenderMixin(object):
	def render_json(self):
		json = {key: value for key, value in self.get_json_params().items() if value not in ('',[],{})}
		self.insert_children_json(json)
		return json

	def get_json_params(self):
		return dict(zip(self.column_names(), self.columns()))

	def insert_children_json(self, json_object):
		pass

class ComboboxEditorMixin(object):
	def getEditor(self, column_number, parent=None):
		if self.columnNames()[column_number] == self._combobox_field:
			from PySide.QtGui import QComboBox, QWidget
			editor = QComboBox(parent or QWidget())
			# editor.insertItems(self.get_combobox_choices())
			return editor
		else:
			return super(ComboboxEditorMixin, self).getEditor(column_number, parent)

	def setEditorData(self, editor, column_number):
		if self.columnNames()[column_number] == self._combobox_field:
			combobox_choices = self.get_combobox_choices()
			editor.insertItems(0, combobox_choices)
			editor.setCurrentIndex(combobox_choices.index(self.columns()[column_number]))
		else:
			return super(ComboboxEditorMixin, self).setEditorData(editor, column_number)

	def setModelData(self, editor, model, column_number):
		if self.columnNames()[column_number] == self._combobox_field:
			setattr(self, self._combobox_field, editor.currentText())
		else:
			return super(ComboboxEditorMixin, self).setModelData(editor, model, column_number)

class TreeMixin(object):
	_parent = None

	def __init__(self, *args, **kwargs):
		self._parent = kwargs.pop('parent', None)
		super(TreeMixin, self).__init__(*args, **kwargs)

	def find_by_id(self, id):
		if self._id == id: # not me!
			return self
		else:
			try:
				return next(child.find_by_id(id) for child in self.children() if child.find_by_id(id))
			except StopIteration:
				return None # not here!

	def parent(self):
		return self._parent # NOTE: it's not because of the OOP incapsulation stuff, but beacause all "public" attrs are considered JSON params

	def parent_form(self):
		from forms import Form

		parent_form = self
		try:
			while not isinstance(parent_form, Form): # go up the tree to closest Form
				parent_form = parent_form.parent()
		except AttributeError:
			raise ValueError('Please select a form before trying to do this')

		return parent_form

	def children(self):
		return []

	def column_names(self):
		def key(name):
			try:
				return ['name', 'type'].index(name)
			except ValueError:
				return 99
		return (name for name in sorted(dir(self), key=key) if not name.startswith('_') and not callable(getattr(self, name)))

	def columns(self):
		return (getattr(self, name) for name in self.column_names())

	def node_kind(self):
		return 'generic'

	def render_tree_json(self):
		return {
			'label': self.name,
			'kind': self.node_kind(),
			'children': [child.render_tree_json() for child in self.children()],
			'id': self._id
		}

	def render_schema(self):
		return OrderedDict(izip(self.column_names(), repeat('Text')))

	def render_data(self):
		return dict(izip(self.column_names(), self.columns()))

	def load_data(self, data):
		updated_params = []
		if self.name != data['name']:
			updated_params.append('name')
		
		self.populate_params(**data)

		return updated_params
