import inspect
import operator
from django.db import models

import forms.models
from misc import BaseFormModel

def get_form_models(for_user=None):
	return inspect.getmembers(
		forms.models, 
		lambda entity: 
			inspect.isclass(entity) and 
			issubclass(entity, BaseFormModel) and 
			not entity == BaseFormModel and
			entity.is_creatable and
			(not for_user or for_user.groups.filter(name__in=entity.user_group_names).exists())
	)

def search_in_queryset(queryset, search_query):
	q_objects = [ models.Q(**{ field_name + '__icontains': search_query }) for field_name in get_search_fields(queryset.model) ]

	return queryset.filter(reduce(operator.or_, q_objects))

def get_search_fields(model):
	return [ 
		field.name for field in model._meta.fields 
		if isinstance(field, models.CharField) 
	]
