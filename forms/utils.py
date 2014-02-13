import inspect

import forms.models
from misc import BaseFormModel

def get_form_models(for_user=None):
	return inspect.getmembers(
		forms.models, 
		lambda entity: 
			inspect.isclass(entity) and 
			issubclass(entity, BaseFormModel) and 
			not entity == BaseFormModel and
			(not for_user or for_user.groups.filter(name=entity.user_group_name).exists())
	)