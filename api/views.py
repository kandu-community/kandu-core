#coding:utf-8

from rest_framework import permissions, generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import serializers
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse, Http404
from django.db import models
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point

from forms.misc import BaseFormModel
from forms.utils import get_form_models, search_in_queryset
import forms.models
from permissions import IsOwnerOrStaff, HasPermission
from serializers import BaseFormSerializer, CustomModelSerializer

class ModelFromUrlMixin(object):
	'''
	Makes API views get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def initial(self, request, *args, **kwargs):
		try:
			self.model = getattr(forms.models, self.kwargs[self.model_url_kwarg])
			self.queryset = self.model.objects.all() # Django REST demands this -_-
		except KeyError:
			pass
		except AttributeError:
			raise exceptions.ParseError('No such form: %s' % self.kwargs[self.model_url_kwarg])

		super(ModelFromUrlMixin, self).initial(request, *args, **kwargs)

class ReadOnlyAndInlinesMixin(object):
	read_only_fields = ('user',)

	def get_serializer_class(self):
		class Meta:
			model = self.model
			read_only_fields = self.read_only_fields
			depth = 1 if self.request.method in ('GET', 'OPTIONS') else 0 # NOTE: kinda dirty hack, better to override serializer instead

		attrs = {
			'Meta': Meta
		}
		if self.model.inlines:
			for inline_name in self.model.inlines:
				class InlineSerializer(serializers.ModelSerializer):
				    class Meta:
				        model = getattr(forms.models, inline_name)
				        read_only_fields = self.read_only_fields

				attrs[inline_name.lower() + '_set'] = InlineSerializer(many=True, read_only=True)

		return type(
			'DefaultSerializer',
			(self.model_serializer_class,),
			attrs
		)

class StaffOmnividenceMixin(object):
	def filter_queryset(self, queryset):
		queryset = super(StaffOmnividenceMixin, self).filter_queryset(queryset)

		if self.request.user.is_staff: # staff sees everything
			return queryset
		else:
			return queryset.filter(user=self.request.user)

class BaseFormList(StaffOmnividenceMixin, generics.ListAPIView):
	'''
	List of all forms submitted by the current user.
	'''

	model = BaseFormModel
	paginate_by = 20
	permission_classes = (permissions.IsAuthenticated,)
	serializer_class = BaseFormSerializer

	def filter_queryset(self, queryset):
		return super(BaseFormList, self).filter_queryset(queryset).select_subclasses()

class FormList(ModelFromUrlMixin, ReadOnlyAndInlinesMixin, StaffOmnividenceMixin, generics.ListCreateAPIView):
	'''
	Submissions of a particular form by the current user.
	'''

	format_kwarg = 'format'
	paginate_by = 20
	permission_classes = (permissions.IsAuthenticated, HasPermission)
	model_serializer_class = CustomModelSerializer

	def pre_save(self, obj):
		obj.user = self.request.user
		super(FormList, self).pre_save(obj)

class FormSearch(ModelFromUrlMixin, ReadOnlyAndInlinesMixin, StaffOmnividenceMixin, generics.ListAPIView):
	paginate_by = 20
	model_serializer_class = CustomModelSerializer

	def filter_queryset(self, queryset):
		parent_queryset = super(FormSearch, self).filter_queryset(queryset)

		try:
			search_query = self.request.GET['query']
		except KeyError:
			raise exceptions.ParseError('You have to supply "query" GET parameter.')

		return search_in_queryset(parent_queryset, search_query)

class FormInRadius(ModelFromUrlMixin, ReadOnlyAndInlinesMixin, StaffOmnividenceMixin, generics.ListAPIView):
	'''
	Submissions with coordinates in a given 'radius' of a given point ('lat' and 'long').
	'''

	paginate_by = 20
	model_serializer_class = CustomModelSerializer

	def filter_queryset(self, queryset):
		parent_queryset = super(FormInRadius, self).filter_queryset(queryset)

		try:
			lat = float(self.request.GET['lat'])
			lng = float(self.request.GET['long'])
			radius = float(self.request.GET['radius'])
		except KeyError:
			raise exceptions.ParseError('You have to supply "lat", "long" and "radius" GET parameters.')

		try:
			return parent_queryset.filter( **{ parent_queryset.model.location_field() + '__distance_lte': (Point(lng, lat), Distance(km=radius)) } )
		except AttributeError as error:
			raise exceptions.ParseError(str(error))

class FormDetail(ModelFromUrlMixin, ReadOnlyAndInlinesMixin, generics.RetrieveUpdateDestroyAPIView):
	'''
	A submitted in form.
	'''

	permission_classes = (IsOwnerOrStaff, HasPermission)
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