from rest_framework import viewsets, generics

import forms.models

class ModelFromUrlMixin(object):
	'''
	Makes API views get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def get_queryset(self):
		model = getattr(forms.models, self.kwargs[self.model_url_kwarg])
		return model.objects.all()

class FormList(ModelFromUrlMixin, generics.ListCreateAPIView):
	def list(self, request, *args, **kwargs):
		if kwargs.has_key(self.model_url_kwarg): #list of forms of the spectific kind
			return super(FormList, self).list(request, *args, **kwargs)
		else: #list of all forms
			raise NotImplementedError

class FormDetail(ModelFromUrlMixin, generics.RetrieveUpdateDestroyAPIView):
	pass
