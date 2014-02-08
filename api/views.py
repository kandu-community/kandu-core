from rest_framework import permissions, generics
from rest_framework import exceptions
from rest_framework import serializers

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

class ReadOnlyFieldsMixin(object):
	read_only_fields = ('user',)

	def get_serializer_class(self):
		class DefaultSerializer(serializers.ModelSerializer):
			class Meta:
				model = self.model
				read_only_fields = self.read_only_fields

		return DefaultSerializer

class FormList(ModelFromUrlMixin, ReadOnlyFieldsMixin, generics.ListCreateAPIView):
	'''
	List of all forms filled by the current user.
	'''

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

	def create(self, request, *args, **kwargs):
		if self.model == BaseFormModel:
			raise exceptions.MethodNotAllowed(self.request.method, detail='You shouldn\'t %s here, use more specific url for that.')
		else:
			return super(FormList, self).create(request, *args, **kwargs)

	def pre_save(self, obj):
		obj.user = self.request.user
		super(FormList, self).pre_save(obj)

class FormDetail(ModelFromUrlMixin, ReadOnlyFieldsMixin, generics.RetrieveUpdateDestroyAPIView):
	'''
	A filled in form.
	'''

	permission_classes = (IsOwner,)