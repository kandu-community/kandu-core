from django.db.models import CharField

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^forms\.fields\.CoordinatesField"])

class CoordinatesField(CharField):
	pass