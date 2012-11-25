# Django settings for a generic project.
import os
from generate_secret_key import generate_secret_key
import dj_database_url

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
	# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

INTERNAL_IPS = ('127.0.0.1',)

# Importing SECRET_KEY from file or generating a new one if missing.
try:
	from secret_key import *
except ImportError:
	generate_secret_key(os.path.join(PROJECT_ROOT, 'secret_key.py'))
	from secret_key import *

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.middleware.gzip.GZipMiddleware',
	'debug_toolbar.middleware.DebugToolbarMiddleware',
	'middleware.ProfileMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

TEMPLATE_DIRS = (
	os.path.join(PROJECT_ROOT, 'reader'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	# "django.core.context_processors.i18n",
	# "django.core.context_processors.media",
	"django.core.context_processors.static",
	# "django.core.context_processors.tz",
	# "django.contrib.messages.context_processors.messages",
	'django.core.context_processors.request',
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	# Uncomment the next line to enable the admin:
	# 'django.contrib.admin',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
	'reader',
	'south',
	'mptt',
	'debug_toolbar',
)

# LOGGING = {
# 	'version': 1,
# 	'disable_existing_loggers': True,
# 	'formatters': {
# 		'standard': {
# 			'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
# 		},
# 	},
# 	'handlers': {
# 		'default': {
# 			'level': 'DEBUG',
# 			'class': 'logging.handlers.RotatingFileHandler',
# 			'filename': 'logs/mylog.log',
# 			'maxBytes': 1024 * 1024 * 5,  # 5 MB
# 			'backupCount': 5,
# 			'formatter': 'standard',
# 		},
# 		'request_handler': {
# 				'level': 'DEBUG',
# 				'class': 'logging.handlers.RotatingFileHandler',
# 				'filename': 'logs/django_request.log',
# 				'maxBytes': 1024 * 1024 * 5,  # 5 MB
# 				'backupCount': 5,
# 				'formatter': 'standard',
# 		},
# 	},
# 	'loggers': {

# 		'': {
# 			'handlers': ['default'],
# 			'level': 'DEBUG',
# 			'propagate': True
# 		},
# 		'django.request': {  # Stop SQL debug from logging to main logger
# 			'handlers': ['request_handler'],
# 			'level': 'DEBUG',
# 			'propagate': False
# 		},
# 	}
# }

# AppFog database connection
if 'VCAP_SERVICES' in os.environ:
	import json
	vcap_services = json.loads(os.environ['VCAP_SERVICES'])
	# XXX: avoid hardcoding here
	psql_srv = vcap_services['mysql-5.1'][0]
	cred = psql_srv['credentials']
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.mysql',
			'NAME': cred['name'],
			'USER': cred['user'],
			'PASSWORD': cred['password'],
			'HOST': cred['hostname'],
			'PORT': cred['port'],
			}
		}
else:
	# Heroku and local database
	DATABASES = {'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))}
