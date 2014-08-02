from mixins import *
from fields import load_field, get_field_class


def load_form(json_object, parent):
	return Form(parent=parent, **json_object)

class Form(TreeMixin, JSONRenderMixin, ParamsMixin, Base):
	name = str()
	category = str()
	user_groups = list()
	is_editable = False

	_fields = None
	_inlines = None

	def __init__(self, *args, **kwargs):
		for mandatory_field in ['name']:
			if mandatory_field not in kwargs:
				raise ValueError('Form is missing %r param. This info might help you locate the form: %r' % (mandatory_field, kwargs))

		self._inlines_container = InlinesContainer(parent=self)

		self._fields = [load_field(field_object, parent=self) for field_object in kwargs.pop('fields', [])]
		self._inlines = [load_form(form_object, parent=self._inlines_container) for form_object in kwargs.pop('inlines', [])]

		super(Form, self).__init__(*args, **kwargs)

	def children(self):
		return self._fields + [self._inlines_container]

	def insertChild(self, datatype):
		FieldClass = get_field_class(datatype)
		self._fields.append(FieldClass(parent=self, name='New field', type=datatype))
		return self._fields[-1]

	def removeChildren(self, node):
		self._fields.remove(node)

	def insert_children_json(self, json_object):
		json_object['fields'] = [field.render_json() for field in self._fields]
		json_object['inlines'] = [form.render_json() for form in self._inlines]

	def render_schema(self):
		schema = super(Form, self).render_schema()
		schema['is_editable'] = 'Checkbox'
		schema['user_groups'] = 'List'
		return schema

class InlinesContainer(TreeMixin, Base):
	name = 'inlines'

	def children(self):
		return self._parent._inlines

	def insertChild(self):
		self._parent._inlines.append(Form(name='New inline form', parent=self))
		return self._parent._inlines[-1]

	def removeChildren(self, node):
		self._parent._inlines.remove(node)

class RootContainer(TreeMixin, JSONRenderMixin, Base):
	name = 'config'

	_forms = []

	def __init__(self, json_object, *args, **kwargs):
		self._forms = [load_form(form_object, parent=self) for form_object in json_object]
		super(RootContainer, self).__init__(*args, **kwargs)

	def children(self):
		return self._forms

	def insertChild(self):
		self._forms.append(Form(parent=self, name='New form', category='Default'))
		return self._forms[-1]

	def removeChildren(self, node):
		self._forms.remove(node)

	def render_json(self):
		return [form.render_json() for form in self._forms]

	def render_tree_json(self):
		return [child.render_tree_json() for child in self.children()]