from functions import generate_name


class Base(object): # workaround for "object.__init__() takes no parameters"
	def __init__(self, *args, **kwargs):
		pass

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

class QtMixin(object):
	_parent = None

	def __init__(self, *args, **kwargs):
		self._parent = kwargs.pop('parent', None)
		super(QtMixin, self).__init__(*args, **kwargs)

	def parent(self):
		return self._parent # NOTE: it's not besause of the OOP incapsulation stuff, but beacause all "public" attrs are considered JSON params

	def childNumber(self):
		return self._parent.children().index(self)

	def columnNames(self):
		names_order = ['name', 'type']
		return sorted(dir(self), key = lambda name: names_order.index(name) if names_order.index(name) != -1 else 99)

	def columns(self):
		return [getattr(self, name) for name in self.columnNames() if not name.startswith('_') and not callable(getattr(self, name))]

	def columnCount(self):
		return len(self.columns())

	def rowCount(self):
		return len(self.children())