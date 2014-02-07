from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm

import forms.models
from forms.utils import get_form_models
from forms.misc import BaseFormModel

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

class FormCreate(SuccessRedirectMixin, ModelFromUrlMixin, CreateView):
	template_name = 'web/form_create.html'

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(FormCreate, self).form_valid(form)

class FormUpdate(SuccessRedirectMixin, ModelFromUrlMixin, UpdateView):
	template_name = 'web/form_update.html'

class FormDelete(SuccessRedirectMixin, ModelFromUrlMixin, DeleteView):
	template_name = 'web/form_delete.html'

class UserRegistration(SuccessRedirectMixin, CreateView):
	template_name = 'web/user_registration.html'
	form_class = UserCreationForm