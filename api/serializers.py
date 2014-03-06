from rest_framework import serializers
from django.core.urlresolvers import reverse

from forms.misc import BaseFormModel
from forms.fields import CoordinatesField as forms_CoordinatesField
from multiselectfield import MultiSelectField as model_MultiSelectField
from fields import CoordinateField, MultiSelectField

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
		return reverse('api_detail', kwargs={'model_name': obj.model_name(), 'pk': obj.pk})

class CustomModelSerializer(serializers.ModelSerializer):
	'''
	Adds MultiSelectField to default mapping.
	'''

	def get_field(self, model_field):
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

			kwargs['choices'] = model_field.flatchoices
			if model_field.null:
				kwargs['empty'] = None
			return MultiSelectField(**kwargs)
		else:
			return super(CustomModelSerializer, self).get_field(model_field)