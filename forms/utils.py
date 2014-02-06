import inspect

import forms.models
from misc import FormModel

def get_form_models():
	return inspect.getmembers(
		forms.models, 
		lambda entity: inspect.isclass(entity) and issubclass(entity, FormModel) and not entity == FormModel
	)