from django.contrib import admin
import inspect

from misc import FormModel
import forms.models

def get_form_models():
	return inspect.getmembers(
		forms.models, 
		lambda entity: inspect.isclass(entity) and issubclass(entity, FormModel) and not entity == FormModel
	)

for form_model in get_form_models():
	admin.site.register(form_model)
