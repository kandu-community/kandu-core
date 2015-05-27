"""
Django settings for kandu project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$m(e@%0_pi5lypls45+pja7t3bt02faf@awewjekhvg)8qwhawse'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'rest_framework.authtoken',
    'bootstrap3',
    'gmapi',
    'south',
    'autocomplete_light',
    'sorl.thumbnail',
    'raven.contrib.django.raven_compat',
    'forms',
    'web',
    'api',
    'icons',
    'config_editor'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'kandu.urls'

WSGI_APPLICATION = 'kandu.wsgi.application'

import json
server_config = json.load(open(os.path.join(BASE_DIR, 'server_config.json')))

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

database_config = {'ENGINE': 'django.contrib.gis.db.backends.postgis'}
database_config.update(server_config['DATABASE'])
DATABASES = {'default': database_config}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/web/login/'
LOGIN_REDIRECT_URL = '/web/'

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = server_config.get('STATIC_ROOT', '/opt/kandu-static/')
MEDIA_ROOT =  server_config.get('MEDIA_ROOT', '/opt/kandu-media/')

TEMPLATE_DIRS = os.path.join(BASE_DIR, 'templates')

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "icons.context_processors.icons",
    "web.context_processors.form_models"
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'PAGINATE_BY': 10,                 # Default to 10
    'PAGINATE_BY_PARAM': 'page_size',  # Allow client to override, using `?page_size=xxx`.
    'MAX_PAGINATE_BY': 1000             # Maximum limit allowed when using `?page_size=xxx`.
}

import sys
LOGGING = {
    'version': 1,
    'handlers': {
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

GEOIP_LIBRARY_PATH = server_config.get('GEOIP_LIBRARY_PATH', '/usr/lib64/libGeoIP.so')
GMAPI_JQUERY_URL = "None" # workaround for jQuery conflict
GMAPI_MAPS_URL = '//maps.google.com/maps/api/js?sensor=false' # a protocol-relative url, to support both http and https

RAVEN_CONFIG = {
    'dsn': 'https://bdd1868a423340acbfb1a17d557b8312:da41c8aa10b6430587de1f59a16ebe9c@app.getsentry.com/32300',
}
