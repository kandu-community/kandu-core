import inspect

import forms.models
from misc import BaseFormModel

def get_form_models():
	return inspect.getmembers(
		forms.models, 
		lambda entity: inspect.isclass(entity) and issubclass(entity, BaseFormModel) and not entity == BaseFormModel
	)