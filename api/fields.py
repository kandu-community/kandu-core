from rest_framework import fields
import json

class CoordinateField(fields.WritableField):
	def to_native(self, value):
		return json.loads(value)

	def from_native(self, value):
		return json.dumps(map(float, value.split(',')))