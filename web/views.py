from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.forms.models import modelform_factory
from django.forms import Form, FileField
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.conf import settings
import os

import forms.models
from forms.utils import get_form_models
from forms.misc import BaseFormModel
from forms.fields import CoordinatesField

class ModelFromUrlMixin(object):
	'''
	Makes CreateView, ListView, etc. get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def get_queryset(self):
		model = getattr(forms.models, self.kwargs[self.model_url_kwarg])
		return model.objects.all()

class ExcludeFieldsMixin(object):
	'''
	Generates form from models, exculuding the fields
	needed to be excluded (eg. 'user', coordinates fields)
	'''

	def get_form_class(self):
		exclude_fields = ['user'] + [ field.name for field in self.get_queryset().model._meta.fields if isinstance(field, CoordinatesField) ]
		return modelform_factory(self.get_queryset().model, exclude=exclude_fields)

class SuccessRedirectMixin(object):
	def get_success_url(self):
		return reverse('web_list')

class FormList(ListView):
	template_name = 'web/form_list.html'
	paginate_by = 20
	
	def get_queryset(self):
		return BaseFormModel.objects.filter(user=self.request.user).select_subclasses()

	def get_context_data(self, **kwargs):
		'''
		Adds a list of defined form models to template context.
		'''
		context = super(FormList, self).get_context_data(**kwargs)

		context['form_models'] = get_form_models()
		return context

class FormCreate(ExcludeFieldsMixin, SuccessRedirectMixin, ModelFromUrlMixin, CreateView):
	template_name = 'web/form_create.html'

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(FormCreate, self).form_valid(form)

class FormUpdate(ExcludeFieldsMixin, SuccessRedirectMixin, ModelFromUrlMixin, UpdateView):
	template_name = 'web/form_update.html'

class FormDelete(SuccessRedirectMixin, ModelFromUrlMixin, DeleteView):
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

		models_filename = os.path.join(settings.BASE_DIR, 'forms', 'models.py')
		with open(models_filename, 'w') as models_file:
			models_file.write(config_to_models(form.cleaned_data['config_file']))

		messages.success(self.request, "Config updated successfully")
		return HttpResponseRedirect(reverse('web_config'))

	def restart_server(self):
		from subprocess import call
		call(['touch', os.path.join(settings.BASE_DIR, 'kandu', 'wsgi.py')])

	def make_migration(self):
		self.restart_server()

		try:
			call_command('schemamigration', 'forms', auto=True)
		except SystemExit:
			pass
		messages.success(self.request, "Migration made successfully")
		return HttpResponseRedirect(reverse('web_config', kwargs={'operation': 'migrate'}))

	def migrate(self):
		call_command('migrate')

		messages.success(self.request, "Migration applied successfully")
		return HttpResponseRedirect(reverse('web_config'))