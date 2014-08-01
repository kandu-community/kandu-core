import pickle
import json
import settings

from forms import misc


def get_root():
	try:
		with open(settings.EDITOR_PICKLE_FILE) as root_dump:
			root = pickle.load(root_dump)
		return root
	except IOError:
		with open(settings.CONFIG_FILE) as config_file:
			root = misc.load_root(json.load(config_file))
		with open(settings.EDITOR_PICKLE_FILE, 'w') as root_dump:
			pickle.dump(root, root_dump)
		return root

def save_root(root):
	with open(settings.EDITOR_PICKLE_FILE, 'w') as root_dump:
		pickle.dump(root, root_dump)