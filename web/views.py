from django.shortcuts import render
from django.forms.models import modelform_factory

import forms.models

class ModelFromUrlMixin(object):
	'''
	Makes CreateViev, UpdateView, etc. get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def get_form_class(self):
		return modelform_factory(getattr(forms.models, self.kwargs[self.model_url_kwarg]))
