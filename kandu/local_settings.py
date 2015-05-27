from settings import *

DEBUG = True

WSGI_APPLICATION = None

MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'local_media', 'media')
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'local_media', 'static')

GEOIP_LIBRARY_PATH = None

RAVEN_CONFIG = {
	'dsn': 'disabled'
}