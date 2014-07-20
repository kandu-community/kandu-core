from functions import config_update_wrapper
try:
	from models import BaseFormModel
except ImportError:
	pass # probably can't import Django, probably we don't need it


from forms import RootContainer


def load_root(json_object):
	return RootContainer(json_object)