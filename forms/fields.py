from multiselectfield import MultiSelectField as broken_MultiSelectField


class MultiSelectField(broken_MultiSelectField):
	@property
	def flatchoices(self):
		return [choice[0] for choice in self.get_choices()]