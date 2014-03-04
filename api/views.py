#coding:utf-8

from rest_framework import permissions, generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import serializers
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse

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

class BaseFormList(generics.ListAPIView):
	'''
	List of all forms submitted by the current user.
	'''

	model = BaseFormModel
	paginate_by = 20
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = BaseFormSerializer

	def filter_queryset(self, queryset):
		if self.request.user.is_staff: # staff sees everything
			return queryset.select_subclasses()
		else:
			return queryset.filter(user=self.request.user).select_subclasses()

class FormList(ModelFromUrlMixin, ReadOnlyFieldsMixin, generics.ListCreateAPIView):
	'''
	Submissions of a particular form by the current user.
	'''

	format_kwarg = 'format'
	paginate_by = 20
	permission_classes = (permissions.IsAuthenticated,)

	def filter_queryset(self, queryset):
		if self.request.user.is_staff: # staff sees everything
			return queryset
		else:
			return queryset.filter(user=self.request.user)

	def pre_save(self, obj):
		obj.user = self.request.user
		super(FormList, self).pre_save(obj)

class FormDetail(ModelFromUrlMixin, ReadOnlyFieldsMixin, generics.RetrieveUpdateDestroyAPIView):
	'''
	A submitted in form.
	'''

	permission_classes = (IsOwnerOrStaff,)
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

class DownloadConfig(generics.GenericAPIView):
	def get(self, request, *args, **kwargs):
		return HttpResponse(open(settings.CONFIG_FILE), content_type='application/json')