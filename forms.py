from mixins import *
from fields import load_field


def load_form(json_object, parent):
	return Form(parent=parent, **json_object)

class Form(QtMixin, ParamsMixin, Base):
	name = str()
	category = str()
	user_groups = list()
	is_editable = None

	_fields = None
	_inlines = None

	def __init__(self, *args, **kwargs):
		for mandatory_field in ['name', 'category']:
			if mandatory_field not in kwargs:
				raise ValueError('Form is missing %r param. This info might help you locate the form: %r' % (mandatory_field, kwargs))

		self._inlines_container = InlinesContainer(parent=self)

		self._fields = [load_field(field_object, parent=self) for field_object in kwargs.pop('fields')]
		self._inlines = [load_form(form_object, parent=self._inlines_container) for form_object in kwargs.pop('inlines', [])]

		super(Form, self).__init__(*args, **kwargs)

	def children(self):
		return self._fields + [self._inlines_container]

class InlinesContainer(QtMixin, Base):
	name = 'inlines'

	def children(self):
		self._parent.inlines

class RootContainer(QtMixin, Base):
	name = 'config'

	_forms = []

	def __init__(self, json_object):
		self._forms = [load_form(form_object, parent=self) for form_object in json_object]

	def children(self):
		return self._forms