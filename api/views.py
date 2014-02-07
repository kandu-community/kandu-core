from rest_framework import permissions, generics

from forms.misc import BaseFormModel
import forms.models

class ModelFromUrlMixin(object):
	'''
	Makes API views get model name from
	url argument insted of "model" class attribute
	'''

	model_url_kwarg = 'model_name'

	def initial(self, request, *args, **kwargs):
		try:
			self.model = getattr(forms.models, self.kwargs[self.model_url_kwarg])
		except KeyError:
			pass

class FormList(ModelFromUrlMixin, generics.ListCreateAPIView):
	model = BaseFormModel
	format_kwarg = 'format'
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		if not self.model:
			return BaseFormModel.objects.filter(user=self.request.user).select_subclasses()
		else:
			return super(FormList, self).get_queryset()

class FormDetail(ModelFromUrlMixin, generics.RetrieveUpdateDestroyAPIView):
	pass
