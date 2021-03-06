import inspect
import operator
from django.db import models

from misc import BaseFormModel

def get_form_models(for_user=None):
	import forms.models
	return inspect.getmembers(
		forms.models, 
		lambda entity: 
			inspect.isclass(entity) and 
			issubclass(entity, BaseFormModel) and 
			not entity == BaseFormModel and
			(not for_user or for_user.groups.filter(name__in=entity.user_group_names).exists())
	)

def search_in_queryset(queryset, search_query, limit=None):
	q_objects = [ models.Q(**{ field_name + '__icontains': search_query }) for field_name in get_search_fields(queryset.model) ]
	try:
		full_queryset = queryset.filter(reduce(operator.or_, q_objects))
		return full_queryset[:limit] if limit else full_queryset
	except TypeError:
		return []

def get_search_fields(model):
	lookup_names = []
	for field in (field for field in model._meta.fields if field.name in getattr(model, 'label_fields', [])):
		if isinstance(field, models.ForeignKey):
			field_names = [
				field.name + '__' + foreign_label_field for foreign_label_field 
				in getattr(field.related.parent_model, 'label_fields', [])
			]
		else:
			field_names = [field.name]

		lookup_names += field_names

	return lookup_names

def clear_app_cache(*apps):
	import os
	from django.db.models.loading import AppCache
	cache = AppCache()

	curdir = os.getcwd()

	for app in cache.get_apps():
		if app.__name__ in apps or len(apps) == 0:
			f = app.__file__
			if f.startswith(curdir) and f.endswith('.pyc'):
				os.remove(f)
			__import__(app.__name__)
			reload(app)

	from django.utils.datastructures import SortedDict
	cache.app_store = SortedDict()
	cache.app_models = SortedDict()
	cache.app_errors = {}
	cache.handled = set()
	cache.loaded = False
