from multiselectfield import MultiSelectField as broken_MultiSelectField

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^forms\.fields\.MultiSelectField"])


class MultiSelectField(broken_MultiSelectField):
	@property
	def flatchoices(self):
		return [choice[0] for choice in self.get_choices()]