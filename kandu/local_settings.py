from settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'kandu',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
    }
}

WSGI_APPLICATION = None

MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'local_media', 'media')
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'local_media', 'static')

GEOIP_LIBRARY_PATH = None