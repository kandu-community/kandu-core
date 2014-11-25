from itertools import izip

from mixins import *
from fields import load_field, get_field_class, ForeignKey


def load_form(json_object, parent):
	return Form(parent=parent, **json_object)

class Form(TreeMixin, JSONRenderMixin, Base):
	name = str()
	category = str()
	user_groups = list()
	is_editable = False
	is_creatable = True
	show_on_map = False

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

	def populate_params(self, **kwargs):
		for label_field_name in kwargs.pop('fields_for_label', []):
			field = next(field for field in self._fields if field.name == label_field_name)
			field.label_field = True
		super(Form, self).populate_params(**kwargs)

	def children(self, for_editing=False):
		if len(self._inlines_container.children()) > 0 and not for_editing: # there are inlines
			return self._fields + [self._inlines_container] # show "inlines" node
		else:
			return self._fields

	def insertChild(self, datatype='text'):
		FieldClass = get_field_class(datatype)
		self._fields.append(FieldClass(parent=self, name='New field', type=datatype))
		return self._fields[-1]

	def change_field_type(self, field_object, new_datatype):
		self._fields.remove(field_object)

		FieldClass = get_field_class(new_datatype)
		new_field_object = FieldClass(parent=self, name=field_object.name, id=field_object._id)
		self._fields.append(new_field_object)
		for param, value in izip(field_object.column_names(), field_object.columns()): # transfer as much data as possible to a new instance
			if param == 'type':
				continue

			if hasattr(new_field_object, param): # if applicable
				setattr(new_field_object, param, value)

		return new_field_object

	def removeChildren(self, node):
		self._fields.remove(node)

	def insert_children_json(self, json_object):
		json_object['fields'] = [field.render_json() for field in self._fields]
		json_object['inlines'] = [form.render_json() for form in self._inlines]

	def render_schema(self):
		schema = super(Form, self).render_schema()
		schema['is_editable'] = 'Checkbox'
		schema['is_creatable'] = 'Checkbox'
		schema['show_on_map'] = 'Checkbox'
		schema['user_groups'] = 'List'
		return schema

class InlinesContainer(ContainerMixin, TreeMixin, Base):
	name = 'inlines'

	def children(self):
		return self._parent._inlines

	def insertChild(self):
		inline_form = Form(name='New inline form', parent=self)
		inline_form._fields.append(ForeignKey(name='parent', to=self._parent.name, parent=inline_form))
		self._parent._inlines.append(inline_form)
		return self._parent._inlines[-1]

	def removeChildren(self, node):
		self._parent._inlines.remove(node)

class RootContainer(ContainerMixin, TreeMixin, JSONRenderMixin, Base):
	name = 'config'

	_forms = []

	def __init__(self, json_object, *args, **kwargs):
		self._forms = [load_form(form_object, parent=self) for form_object in json_object]
		super(RootContainer, self).__init__(*args, **kwargs)

	def children(self, for_editing=False):
		return self._forms

	def insertChild(self):
		self._forms.append(Form(parent=self, name='New form', category='Default'))
		return self._forms[-1]

	def removeChildren(self, node):
		self._forms.remove(node)

	def moveChild(self, node, previous_parent, target, position):
		new_parent = target if position == 'inside' else target.parent()

		from_list = previous_parent.children(for_editing=True)
		to_list = new_parent.children(for_editing=True)

		moved_node = from_list.pop(from_list.index(node))
		to_list.insert(0 if position == 'inside' else (to_list.index(target) + int(position == 'after')), moved_node)

		node._parent = new_parent

	def render_json(self):
		return [form.render_json() for form in self._forms]

	def render_tree_json(self):
		return [child.render_tree_json() for child in self.children()]