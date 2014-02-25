#coding:utf-8

from rest_framework import permissions, generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import serializers
import json
from django.core.urlresolvers import reverse

from forms.misc import BaseFormModel
from forms.utils import get_form_models
import forms.models
from permissions import IsOwner
from serializers import BaseFormSerializer, CustomModelSerializer

class ModelFromUrlMixin(object):
	'''
	Makes API views get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def initial(self, request, *args, **kwargs):
		super(ModelFromUrlMixin, self).initial(request, *args, **kwargs)

		try:
			self.model = getattr(forms.models, self.kwargs[self.model_url_kwarg])
		except KeyError:
			pass

class ReadOnlyFieldsMixin(object):
	read_only_fields = ('user',)

	def get_serializer_class(self):
		class DefaultSerializer(self.model_serializer_class):
			class Meta:
				model = self.model
				read_only_fields = self.read_only_fields

		return DefaultSerializer

class FormList(ModelFromUrlMixin, ReadOnlyFieldsMixin, generics.ListCreateAPIView):
	'''
	List of forms submitted by the current user.
	'''

	model = BaseFormModel
	format_kwarg = 'format'
	paginate_by = 20
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		if self.model != BaseFormModel: # model has been overriden by url argument
			return self.model.objects.all()
		else:
			return BaseFormModel.objects.select_subclasses()

	def filter_queryset(self, queryset):
		if self.request.user.is_staff: # staff sees everything
			return queryset
		else:
			return queryset.filter(user=self.request.user)

	def get_serializer_class(self):
		if self.model != BaseFormModel:
			return super(FormList, self).get_serializer_class()
		else:
			return BaseFormSerializer

	def create(self, request, *args, **kwargs):
		if self.model == BaseFormModel:
			raise exceptions.MethodNotAllowed(self.request.method, detail='You shouldn\'t %s here, use more specific url for that.')
		else:
			return super(FormList, self).create(request, *args, **kwargs)

	def pre_save(self, obj):
		obj.user = self.request.user
		super(FormList, self).pre_save(obj)

class FormDetail(ModelFromUrlMixin, ReadOnlyFieldsMixin, generics.RetrieveUpdateDestroyAPIView):
	'''
	A submitted in form.
	'''

	permission_classes = (IsOwner,)
	model_serializer_class = CustomModelSerializer

class AvailableForms(generics.GenericAPIView):
	def get(self, request, *args, **kwargs):
		forms_dicts = [
				{
					'name': form_name,
					'verbose_name': form_class.verbose_name(),
					'url': reverse('api_list', kwargs={'model_name':form_name})
				}
			for form_name, form_class in get_form_models(for_user=self.request.user) 
		]
		return Response(forms_dicts)