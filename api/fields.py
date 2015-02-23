import json
from django.core import exceptions, validators
from django.contrib.gis.geos import Point
from rest_framework.fields import CharField
try:
	from rest_framework.fields import MultipleChoiceField as rest_ChoiceField
except ImportError: # django rest framework < 3.x
	from rest_framework.fields import ChoiceField as rest_ChoiceField


class CoordinatesField(CharField):
	type_label = 'coordinates'

	def to_native(self, obj):
		if obj == None:
			return None

		longitude, lattitude = obj.coords
		return (lattitude, longitude)

	def from_native(self, data):
		if data in validators.EMPTY_VALUES:
			return None

		if isinstance(data, basestring):
			lattitude, longitude = map(float, data.split(','))
		else:
			lattitude, longitude = data

		return Point(longitude, lattitude)

class MultiSelectField(rest_ChoiceField):
	type_label = 'multiple choice (multi-select)'

	def to_internal_value(self, data):
		return list(data)

	def to_representation(self, value):
		return value

	def validate(self, value):
		if value in validators.EMPTY_VALUES:
			if self.required:
				raise exceptions.ValidationError(self.error_messages['required'])
			else: # empty and not requred - okay
				return

		if isinstance(value, basestring): #we got a list in a form of string
			value = value.split(',')

		arr_choices = [ short for short, full in self.choices ]
		for opt_select in value:
			if opt_select not in arr_choices:
				raise exceptions.ValidationError(self.error_messages['invalid_choice'], params={"value": opt_select})
