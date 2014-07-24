from functions import generate_name


class Base(object): # workaround for "object.__init__() takes no parameters"
	def __init__(self, *args, **kwargs):
		pass

class DjangoRenderMixin(object):
	def get_django_args(self):
		django_args = {name: getattr(self, name) for name in dir(self) if not name.startswith('_') and not callable(getattr(self, name))}
		django_args['blank'] = not django_args.pop('required')
		django_args['help_text'] = django_args.pop('hint')

		for name in ['visible_when', 'type', 'name']:
			django_args.pop(name)
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
		return dict(zip(self.columnNames(), self.columns()))

	def insert_children_json(self, json_object):
		pass

class ParamsMixin(object):
	def __init__(self, *args, **kwargs):
		super(ParamsMixin, self).__init__(*args, **kwargs)
		self.populate_params(**kwargs)

	def populate_params(self, **kwargs):
		for name, value in kwargs.items():
			if hasattr(self, name):
				setattr(self, name, value)
			else:
				from fields import Field
				raise ValueError('Unknown parameter %r for %s %r' % (name, 'field' if isinstance(self, Field) else 'form', kwargs['name']))

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

class QtMixin(object):
	_parent = None

	def __init__(self, *args, **kwargs):
		self._parent = kwargs.pop('parent', None)
		super(QtMixin, self).__init__(*args, **kwargs)

	def parent(self):
		return self._parent # NOTE: it's not because of the OOP incapsulation stuff, but beacause all "public" attrs are considered JSON params

	def children(self):
		return []

	def childNumber(self):
		return self._parent.children().index(self)

	def columnNames(self):
		def key(name):
			try:
				return ['name', 'type'].index(name)
			except ValueError:
				return 99
		return [name for name in sorted(dir(self), key=key) if not name.startswith('_') and not callable(getattr(self, name))]

	def columns(self):
		return [getattr(self, name) for name in self.columnNames()]

	def columnCount(self):
		return len(self.columns())

	def rowCount(self):
		return len(self.children())

	def getEditor(self, column_number, parent=None):
		return None