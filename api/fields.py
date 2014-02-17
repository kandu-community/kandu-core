from rest_framework import fields
import json
from django.core import exceptions

class CoordinateField(fields.WritableField):
	def to_native(self, value):
		return json.loads(value)

	def from_native(self, value):
		return json.dumps(map(float, value.split(',')))

class MultiSelectField(fields.ChoiceField):
    def validate(self, value):
        arr_choices = [ short for short, full in self.choices ]
        for opt_select in value:
            if (opt_select not in arr_choices):
                raise exceptions.ValidationError(self.error_messages['invalid_choice'] % {"value": value})
