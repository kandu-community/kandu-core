#coding:utf-8

from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import modelform_factory
from django.forms import Form, FileField, Field, Form
from django.contrib.auth.models import Group
from django.db.models import ForeignKey
from django.core.management import call_command
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import os
from gmapi import maps
from gmapi.forms.widgets import GoogleMap
import autocomplete_light
from django.db import models
from django.contrib.gis.geoip import GeoIP
from django.contrib.gis.db.models import PointField
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView

import forms.models
from forms.utils import get_form_models, get_search_fields
from forms.misc import BaseFormModel

class ModelFromUrlMixin(object):
	'''
	Makes CreateView, ListView, etc. get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'
	inlines_also = False

	def dispatch(self, *args, **kwargs):
		try:
			self.model = getattr(forms.models, self.kwargs[self.model_url_kwarg])
		except AttributeError:
			return HttpResponseNotFound("No such form: %s" % self.kwargs[self.model_url_kwarg])

		if self.inlines_also and self.model.inlines:
			self.inlines = []
			for inline_model_name in self.model.inlines:
				inline_model = getattr(forms.models, inline_model_name)

				class FormModelInline(InlineFormSet):
					model = inline_model
					fk_name = next( field.name for field in inline_model._meta.fields if isinstance(field, ForeignKey) and field.rel.to == self.model and field.name != 'baseformmodel_ptr_id' )
					exclude = ('user',)
					extra = 1 # since we got dynamic "add another"

				self.inlines.append(FormModelInline)

		return super(ModelFromUrlMixin, self).dispatch(*args, **kwargs)

class InlineDefaultValueMixin(object):
	def forms_valid(self, form, inlines):
		if not form.instance.user_id:
			form.instance.user = self.request.user
		self.object = form.save()

		for formset in inlines:
			for instance in formset.save(commit=False):
				if not instance.user_id:
					instance.user = self.request.user
				instance.save()
					
		return HttpResponseRedirect(self.get_success_url())

class ExcludeFieldsMixin(object):
	'''
	Generates form from models, exculuding the fields
	needed to be excluded (eg. 'user', coordinates fields)
	'''

	def get_exclude_fields(self):
		exclude_fields = ['user', 'created_at'] + \
		[ field.name for field in self.model._meta.fields if isinstance(field, PointField) ]

		return exclude_fields

class SuccessRedirectMixin(object):
	def get_success_url(self):
		return reverse('web_list')

class CheckPermissionsMixin(object):
	def dispatch(self, *args, **kwargs):
		if self.has_permission():
			return super(CheckPermissionsMixin, self).dispatch(*args, **kwargs)
		else:
			return HttpResponseForbidden("You don't have permission to perform this action.")

	def has_permission(self):
		return self.model in [model for name, model in get_form_models(for_user=self.request.user)]

class MapMixin(object):
	def get_context_data(self, **kwargs):
		'''
		Adds a list of forms current user can fill into template context.
		'''
		context = super(MapMixin, self).get_context_data(**kwargs)

		context['map'] = self.get_map()
		return context

	def get_map(self):
		gmap = maps.Map()

		for form_object in self.object_list:
			if form_object.show_on_map:
				try:
					lng, lat = getattr(form_object, form_object.location_field()).coords
					marker = maps.Marker(opts = {
						'map': gmap,
						'position': maps.LatLng(lat, lng),
					})

					maps.event.addListener(marker, 'click', 'myobj.markerOver')
					info = maps.InfoWindow({
						'content': '<a href="{url}">{text}</a>'.format(
							text = form_object.__unicode__(),
							url = reverse('web_update', kwargs={'model_name': form_object.model_name(), 'pk': form_object.pk})
						),
						'disableAutoPan': True
					})
					info.open(gmap, marker)
				except (TypeError, AttributeError): #no coordinates field or it has invalid value
					continue

		class MapForm(Form):
			map = Field(widget=GoogleMap(attrs={'width':800, 'height':550}))

		return MapForm(initial={'map': gmap})

class AutocompleteFormMixin(object):
	def get_form_class(self):
		if self.form_class:
			return self.form_class
		else:
			return autocomplete_light.modelform_factory(
				self.model, 
				autocomplete_fields=[ field.name for field in self.model._meta.fields if isinstance(field, models.ForeignKey) ],
				exclude=getattr(self, 'get_exclude_fields', None)()
			)

class StaffOmnividenceMixin(object):
	def get_queryset(self):
		parent_queryset = super(StaffOmnividenceMixin, self).get_queryset()

		if self.request.user.is_staff:
			return parent_queryset
		else:
			return parent_queryset.filter(user=self.request.user)

class BaseFormList(StaffOmnividenceMixin, ListView):
	template_name = 'web/form_list.html'
	paginate_by = 10
	
	def get_queryset(self):
		return BaseFormModel.objects.order_by('-created_at').select_subclasses()

class MapView(MapMixin, ListView):
	template_name = 'web/map_view.html'
	max_objects = 10

	def get_queryset(self):
		ip_address = self.request.META.get('REMOTE_ADDR', None)

		gi = GeoIP(settings.STATIC_ROOT)
		location = gi.lon_lat(ip_address)

		object_list = []
		for form_name, form_model in get_form_models(for_user=self.request.user):
			if location: # first closest objects
				object_list += list( form_model.objects.distance(Point(location)).order_by('distance')[:self.max_objects] )

			else: # falling back to just first objects
				object_list += list(form_model.objects.order_by('created_at')[:self.max_objects])

		return object_list

class FormList(ModelFromUrlMixin, CheckPermissionsMixin, StaffOmnividenceMixin, ListView):
	template_name = 'web/form_list.html'
	paginate_by = 10

	def get_queryset(self):
		queryset = super(FormList, self).get_queryset()
		return queryset.order_by('-created_at')

	def get_context_data(self, **kwargs):
		context = super(FormList, self).get_context_data(**kwargs)
		context['object_list_model'] = self.object_list.model
		return context

class FormCreate(AutocompleteFormMixin, ExcludeFieldsMixin, SuccessRedirectMixin, InlineDefaultValueMixin, ModelFromUrlMixin, CheckPermissionsMixin, CreateWithInlinesView):
	template_name = 'web/form_create.html'
	inlines_also = True

class FormUpdate(AutocompleteFormMixin, ExcludeFieldsMixin, SuccessRedirectMixin, InlineDefaultValueMixin, ModelFromUrlMixin, CheckPermissionsMixin, UpdateWithInlinesView):
	template_name = 'web/form_update.html'
	inlines_also = True

	def has_permission(self):
		if not self.model.is_editable:
			return False
		else:
			return super(FormUpdate, self).has_permission()

class FormDelete(SuccessRedirectMixin, ModelFromUrlMixin, CheckPermissionsMixin, DeleteView):
	template_name = 'web/form_delete.html'

class UserRegistration(SuccessRedirectMixin, CreateView):
	template_name = 'web/user_registration.html'
	form_class = UserCreationForm

class ManageConfig(FormView):
	template_name = 'web/config_form.html'

	def get(self, request, *args, **kwargs):
		if kwargs.has_key('operation'):
			return getattr(self, kwargs['operation'])()
		else:
			return super(ManageConfig, self).get(request, *args, **kwargs)

	def get_form_class(self):
		class UploadConfigForm(Form):
			config_file = FileField()

		return UploadConfigForm

	def form_valid(self, form):
		from forms.misc import config_to_models

		with open(settings.CONFIG_FILE, 'w') as config_file:
			config_file.write(form.cleaned_data['config_file'].read())

		models_filename = os.path.join(settings.BASE_DIR, 'forms', 'models.py')
		try:
			models_str = config_to_models(open(settings.CONFIG_FILE))
			with open(models_filename, 'w') as models_file:
				models_file.write(models_str)

			self.restart_server()
			messages.success(self.request, "Config updated successfully")
		except ValueError as error:
			messages.error(self.request, str(error))
		return HttpResponseRedirect(reverse('web_config'))

	def restart_server(self):
		from subprocess import call
		call(['touch', os.path.join(settings.BASE_DIR, 'kandu', 'wsgi.py')])

	def make_migration(self):
		# self.restart_server()

		try:
			call_command('schemamigration', 'forms', auto=True)
		except SystemExit:
			pass
		messages.success(self.request, "Migration made successfully")
		return HttpResponseRedirect(reverse('web_config'))

	def migrate(self):
		self.restart_server()

		call_command('migrate', noinput=True)

		messages.success(self.request, "Migration applied successfully")
		return HttpResponseRedirect(reverse('web_config'))