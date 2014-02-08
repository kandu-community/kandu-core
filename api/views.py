from rest_framework import permissions, generics
from rest_framework import exceptions

from forms.misc import BaseFormModel
import forms.models
from permissions import IsOwner
from serializers import BaseFormSerializer

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

class FormList(ModelFromUrlMixin, generics.ListCreateAPIView):
	model = BaseFormModel
	format_kwarg = 'format'
	paginate_by = 20
	permission_classes = (permissions.IsAuthenticated,)

	def get_queryset(self):
		if self.model != BaseFormModel: #model has been overriden by url argument
			return self.model.objects.filter(user=self.request.user)
		else:
			self.serializer_class = BaseFormSerializer
			return BaseFormModel.objects.filter(user=self.request.user).select_subclasses()

class FormDetail(ModelFromUrlMixin, generics.RetrieveUpdateDestroyAPIView):
	permission_classes = (IsOwner,)