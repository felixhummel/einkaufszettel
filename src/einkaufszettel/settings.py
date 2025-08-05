import os
import warnings
from pathlib import Path
import structlog

log = structlog.get_logger()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
log.info('settings', BASE_DIR=BASE_DIR)

# Suppress Pydantic deprecation warnings from django-ninja
# TODO: Remove this when django-ninja updates to use ConfigDict instead of class-based config
warnings.filterwarnings(
    'ignore',
    message='Support for class-based `config` is deprecated.*',
    category=DeprecationWarning,
)

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # https://whitenoise.readthedocs.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django_extensions',
    'felix_django',
    'einkaufszettel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'einkaufszettel.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STORAGES = {
    # https://whitenoise.readthedocs.io/en/stable/django.html
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_DATABASE_NAME'],
        'USER': os.environ['DB_USERNAME'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.environ['STATIC_ROOT']


MEDIA_ROOT = os.environ['MEDIA_ROOT']
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

NINJA_PAGINATION_PER_PAGE = 20

AUTH_USER_MODEL = 'einkaufszettel.user'

# this only comes into play with TLS
# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
_cookie_domain = os.environ.get('COOKIE_DOMAIN', '')
SESSION_COOKIE_DOMAIN = _cookie_domain
# https://docs.djangoproject.com/en/3.2/ref/csrf/#csrf-limitations
CSRF_COOKIE_DOMAIN = _cookie_domain
LANGUAGE_COOKIE_DOMAIN = _cookie_domain
CSRF_COOKIE_SECURE = True
