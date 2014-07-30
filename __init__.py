from functions import config_update_wrapper
try:
	from models import BaseFormModel
except ImportError:
	pass # probably can't import Django, probably we don't need it


import inspect
from forms import RootContainer
import fields


def load_root(json_object):
	return RootContainer(json_object)

def get_available_fields():
	return inspect.getmembers(fields, 
		lambda entity: inspect.isclass(entity) and issubclass(entity, fields.Field) and entity != fields.Field
	)