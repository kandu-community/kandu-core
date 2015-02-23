import rest_framework
from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.gis.db.models import GeometryField as model_GeometryField
from django.contrib.sites.models import get_current_site

from forms.misc import BaseFormModel
from multiselectfield import MultiSelectField as model_MultiSelectField
from fields import MultiSelectField, CoordinatesField

class BaseFormSerializer(serializers.ModelSerializer):
	class Meta:
		model = BaseFormModel

	url = serializers.SerializerMethodField('instance_url')
	description = serializers.SerializerMethodField('instance_unicode')

	def instance_model_name(self, obj):
		return obj.model_name()

	def instance_unicode(self, obj):
		return obj.__unicode__().split(', ')

	def instance_url(self, obj):
		return reverse('api_detail', kwargs={'model_name': obj.model_name(), 'pk': obj.pk}, request=self.context['request'])

class CustomFieldMapping(dict):
	def __getitem__(self, key):
		if issubclass(key, model_GeometryField):
			return CoordinatesField
		elif issubclass(key, model_MultiSelectField):
			return MultiSelectField
		else:
			return super(CustomFieldMapping, self).__getitem__(key)

	def __contains__(self, key):
		if issubclass(key, model_GeometryField):
			return True
		elif issubclass(key, model_MultiSelectField):
			return True
		else:
			return super(CustomFieldMapping, self).__contains__(key)		

class CustomModelSerializer(serializers.ModelSerializer):
	'''
	Adds MultiSelectField to default mapping.
	'''

	if rest_framework.__version__.startswith('2'):
		field_mapping = CustomFieldMapping(serializers.ModelSerializer.field_mapping)
	else:
		serializer_field_mapping = CustomFieldMapping(serializers.ModelSerializer.serializer_field_mapping)

	def get_field(self, model_field): # NOTE: this is for djangorestframework 2.x
		if isinstance(model_field, model_MultiSelectField):
			kwargs = {}

			if model_field.null or model_field.blank:
				kwargs['required'] = False

			if not model_field.editable:
				kwargs['read_only'] = True

			if model_field.has_default():
				kwargs['default'] = model_field.get_default()

			if model_field.verbose_name is not None:
				kwargs['label'] = model_field.verbose_name

			if model_field.help_text is not None:
				kwargs['help_text'] = model_field.help_text

			kwargs['choices'] = model_field.get_choices()
			if model_field.null:
				kwargs['empty'] = None
			return MultiSelectField(**kwargs)
		else:
			return super(CustomModelSerializer, self).get_field(model_field)

	def build_standard_field(self, field_name, model_field):
		field_class, field_kwargs = super(CustomModelSerializer, self).build_standard_field(field_name, model_field)
		if isinstance(model_field, model_MultiSelectField):
			field_class = MultiSelectField
		return field_class, field_kwargs