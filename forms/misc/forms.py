from functions import generate_name
from mixins import *
from fields import load_field


def load_form(json_object):
	return Form(**json_object)

class Form(QtMixin, ParamsMixin, object):
	name = str()
	category = str()
	field_for_label = list()
	user_groups = list()
	is_editable = None

	_fields = []

	def __init__(self, *args, **kwargs):
		self._fields = [load_field(field_object) for field_object in kwargs.pop('fields')]
		self._inlines = [load_form(form_object) for form_object in kwargs.pop('inlines')]

		super(Form, self).__init__(*args, **kwargs)

	def children(self):
		return self._fields + [InlinesContainer(parent=self)]

class InlinesContainer(QtMixin, object):
	name = 'inlines'

	def children(self):
		self._parent.inlines