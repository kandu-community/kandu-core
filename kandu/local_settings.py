from settings import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'kandu',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'password',                  # Not used with sqlite3.
    }
}

WSGI_APPLICATION = None

MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'local_media', 'media')