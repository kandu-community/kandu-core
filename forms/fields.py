from django.db.models import CharField
import re

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^forms\.fields\.CoordinatesField"])

class CoordinatesField(CharField):
	def to_python(self, value):
		if isinstance(value, basestring):
			return map(float, re.findall(r'([\d\.]+)', value))
			
		return value

	def get_prep_value(self, value):
		if isinstance(value, basestring):
			value = re.findall(r'([\d\.]+)', value)

		return ','.join(map(str, value))