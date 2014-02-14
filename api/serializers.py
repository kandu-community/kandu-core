from rest_framework import serializers

from forms.misc import BaseFormModel
from forms.fields import CoordinatesField as forms_CoordinatesField
from fields import CoordinateField

class BaseFormSerializer(serializers.ModelSerializer):
	class Meta:
		model = BaseFormModel

	form_class = serializers.SerializerMethodField('instance_model_name')
	description = serializers.SerializerMethodField('instance_unicode')

	def instance_model_name(self, obj):
		return obj.model_name()

	def instance_unicode(self, obj):
		return obj.__unicode__()

class CustomFieldMapping(dict):
	def __getitem__(self, key):
		if issubclass(key, forms_CoordinatesField):
			return CoordinateField
		return super(CustomFieldMapping, self).__getitem__(key)

class CustomModelSerializer(serializers.ModelSerializer):
	field_mapping = CustomFieldMapping(serializers.ModelSerializer.field_mapping)