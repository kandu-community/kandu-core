from django.conf import settings
import os

EDITOR_PICKLE_FILE = getattr(settings, 'EDITOR_PICKLE_FILE', os.path.join(settings.BASE_DIR, 'config.pickle'))