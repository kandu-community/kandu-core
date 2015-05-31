from django.db.models.fields import CharField
from multiselectfield import MultiSelectField as broken_MultiSelectField

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^forms\.fields\.MultiSelectField"])
add_introspection_rules([], ["^forms\.fields\.DjangoIdField"])


class MultiSelectField(broken_MultiSelectField):
	@property
	def flatchoices(self):
		return [choice[0] for choice in self.get_choices()]

class DjangoIdField(CharField):
	def __init__(self, *args, **kwargs):
		self.from_fields = kwargs.pop('from_fields', [])
		super(DjangoIdField, self).__init__(*args, **kwargs)

	def generate_value(self, obj):
		return '-'.join([
			unicode(getattr(obj, field_name)).upper()[:3]
			for field_name in self.from_fields
		] + [str(obj.id)])