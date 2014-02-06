from django.shortcuts import render
from django.forms.models import modelform_factory
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

import forms.models
from forms.utils import get_form_models

class ModelFromUrlMixin(object):
	'''
	Makes CreateView, ListView, etc. get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def get_queryset(self):
		model = getattr(forms.models, self.kwargs[self.model_url_kwarg])
		return model.objects.all()

class SuccessRedirectMixin(object):
	def get_success_url(self):
		return reverse('web_list')

class FormList(ListView):
	template_name = 'web/form_list.html'
	# paginate_by = 20

	def get_queryset(self):
		user_forms = []
		for form_name, form_model in get_form_models():
			user_forms += form_model.objects.filter(user=self.request.user) 

		return user_forms

	def get_context_data(self, **kwargs):
		'''
		Adds a list of defined form models to template context.
		'''
		context = super(FormList, self).get_context_data(**kwargs)

		context['form_models'] = get_form_models()
		return context

class FormCreate(SuccessRedirectMixin, ModelFromUrlMixin, CreateView):
	template_name = 'web/form_create.html'

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(FormCreate, self).form_valid(form)

class FormUpdate(SuccessRedirectMixin, ModelFromUrlMixin, UpdateView):
	template_name = 'web/form_update.html'

class FormDelete(SuccessRedirectMixin, ModelFromUrlMixin, DeleteView):
	template_name = 'web/form_delete.html'