from django.db.models import CharField

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^forms\.fields\.CoordinatesField"])

class CoordinatesField(CharField):
	def to_python(self, value):
		return map(float, value.split(','))

	def get_prep_value(self, value):
		if isinstance(value, basestring):
			return value

		return ','.join(map(str, value))	