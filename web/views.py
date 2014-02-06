from django.shortcuts import render
from django.forms.models import modelform_factory
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
import inspect

import forms.models

class ModelFromUrlMixin(object):
	'''
	Makes CreateView, ListView, etc. get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def dispatch(self, request, *args, **kwargs):
		self.model = getattr(forms.models, kwargs[self.model_url_kwarg])
		super(ModelFromUrlMixin, self).dispatch(request, *args, **kwargs)

class FormList(ListView):
	template_name = 'web/form_list.html'
	paginate_by = 20

	# def get_queryset(self):
	# 	user_forms = [
	# 		form_class.objects.filter(user=self.request.user) for form_class
	# 		in inspect.getmembers(forms.models, inspect.isclass)
	# 	]

	# 	return user_forms

	def get_context_data(self, **kwargs):
		'''
		Adds a list of defined form models to template context.
		'''
		context = super(FormList, self).get_context_data(**kwargs)
		context['form_models'] = inspect.getmembers(forms.models, inspect.isclass)
		return context

class FormCreate(ModelFromUrlMixin, CreateView):
	pass

class FormUpdate(ModelFromUrlMixin, UpdateView):
	pass

class FormDelete(ModelFromUrlMixin, DeleteView):
	pass